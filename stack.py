#! /usr/bin/env python

import argparse
import commands
import logging
import os
import re
import sys
import time

import client
import config
import create
import delete
import logs
import ssh
import wait

logging.getLogger(__name__).addHandler(logging.StreamHandler())

log = logs.logger('Stack')

args_parser = argparse.ArgumentParser(
    prog='stack.py',
    description='Containers tempest devstack vm setup',
    formatter_class=argparse.RawTextHelpFormatter)
args_parser.add_argument(
    '-r', '--reset',
    action='store_true',
    dest='reset',
    default=False,
    required=False,
    help='delete existing vm and start from scratch')
args_parser.add_argument(
    '-d', '--devstack-only',
    action='store_true',
    dest='devstack_only',
    default=False,
    required=False,
    help='just run devstack on an existing vm')

meta = dict()
image = None
flavor = None
private_key = './id_rsa'
public_key = './id_rsa.pub'
name_prefix = 'devstack-tempest'

def stack_vm():
    fetch_image()
    fetch_flavor()
    server = None
    name = '{}-{}'.format(name_prefix, time.time())
    try:
        files = {
            '/root/.ssh/authorized_keys': public_key_file(),
            '/root/bootstrap.sh': content('scripts/bootstrap.sh')
        }
        server = create(name, files=files)
        ping(server)
        log.info('Created server {}'.format(server.name))
        return server
    except KeyboardInterrupt as ex:
        print 'Interrupted'
        sys.exit(0)

# Upgrade the server, install git and pip packages, add tox via pip 
# (because the packaged version is too old), set up a "jenkins" account 
# (add user "jenkins" to sudoers) and reboot to make sure you're 
# running a current kernel:
def config_stack_vm(server):
    remote(server, command='cp /root/.ssh/authorized_keys /root/.ssh/id_rsa.pub')
    remote(server, command='chmod +x /root/bootstrap.sh')
    # remote(server, command='nohup /root/bootstrap.sh 2>&1')
    remote(server, command='/root/bootstrap.sh &')
    wait_for_file(server, '/tmp/openstack-infra-finished', user='root')

    if config.libvirt_type == 'lxc':
        remote(server, command='nohup /tmp/a/scripts/nbd-install.sh 2>&1')
    remote(server, command='reboot')

    log.info("Pausing 60 seconds for server to finish rebooting")
    time.sleep(60)
    wait.until_up(server, user='jenkins', timeout=1000, interval=5, keyfile=private_key)

def config_devstack_zuul_target(server):
    if not (config.zuul_url and config.zuul_project and config.zuul_branch):
        return

    overrides = {
        'REPO_URL': config.repo_url,
        'ZUUL_URL': config.zuul_url,
        'ZUUL_PROJECT': config.zuul_project,
        'ZUUL_BRANCH': config.zuul_branch,
        'DEVSTACK_GATE_LIBVIRT_TYPE': config.libvirt_type,
        'DEVSTACK_GATE_TEMPEST_REGEX': config.devstack_regex
    }

    command = 'cat << EOF > $HOME/scripts/jenkins-devstack-env-overrides.sh'

    for key,value in overrides.items():
        if value:
            command = "{}\nexport {}={}".format(command, key, value)

    command = "{}\nEOF".format(command)

    remote(server, user='jenkins', command=command)

def vm_devstack(server):
    #remote(server, user='jenkins', command='nohup $HOME/scripts/jenkins-devstack.sh 2>&1 &')
    remote(server, user='jenkins', command='$HOME/scripts/jenkins-devstack.sh &')
    # remote(server, user='jenkins', command="screen -S jenkins-devstack -X '$HOME/scripts/jenkins-devstack.sh' 'cmd^M'")
    wait_for_file(server, '/tmp/gate-finished')
    print_devstack_log(server)
    return_code = int(remote(server, user='jenkins', command='cat /tmp/gate-finished'))
    log.info("Exiting with return code {}".format(return_code))
    print 'Finished running devstack tempest tests on {}'.format(server.accessIPv4)
    sys.exit(return_code)

def wait_for_file(server, f, user='jenkins'):
    log.info('Waiting for file {}...'.format(f))
    limit = time.time() + 30000
    try:
        while time.time() < limit:
            time.sleep(20)
            result = ''
            try:
                pass
                result = remote(server, user=user, command='[[ -f {} ]] && echo done'.format(f))
            except Exception as ex:
                log.error("Error waiting for file {}: {}".format(f, ex.message))
            if len(result) > 0:
                return
        log.warning('Timed out waiting for {}'.format(f))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

def print_devstack_log(server):
    if not server:
        return
    target = server.accessIPv4
    result = ssh.fetch(target, '/home/jenkins/devstack-gate-log.txt', user='jenkins', keyfile=private_key)
    if result:
        print result

def find(f, seq):
    for item in seq:
        if f(item): 
            return item

def find_server(pattern):
    servers = client.nova.servers.list()
    return find(lambda server: re.compile(pattern).match(server.name), servers)

def setup():
    server = find_server('^{}-.*'.format(name_prefix))
    if not server:
        server = stack_vm()
    log.info("Pausing 120 seconds for ssh server to start on {}".format(server.id))
    time.sleep(120) # Wait for ssh server to start?
    wait.until_up(server, timeout=1000, interval=5, keyfile=private_key)
    return server

def reset():
    server = find_server('^{}-.*'.format(name_prefix))
    if server:
        delete.delete(server.id)
        wait.until_gone(server)

def fetch_flavor():
    global flavor
    try:
        flavor = client.nova.flavors.get(config.flavor)
    except Exception as ex:
        log.error('Failed to fetch flavor {} {}'.format(config.flavor, ex.message))
        sys.exit(1)

def fetch_image():
    global image
    try:
        image = client.nova.images.get(config.image)
    except Exception as ex:
        log.error('Failed to fetch image {} {}'.format(config.image, ex.message))
        sys.exit(1)

def create(name, key_name=None, files=dict()):
    log.info('Creating server {}'.format(name))
    server = client.nova.servers.create(name, image, flavor, key_name=key_name, meta=meta, files=files)
    log.info('Created server {} with password {}'.format(server.id, server.adminPass))
    if wait.has_state(server, 'ACTIVE', config.timeout, silently=True):
        log.info('Server has started with IP address {}'.format(server.accessIPv4 or server.addresses['private'][0]['addr']))
    return server

def remote(server, user='root', command=config.command):
    if not server:
        return
    name = server.name
    target = server.accessIPv4
    result = ssh.remote_exec(target, user=user, keyfile=private_key, command=command)
    if result:
        log.info(result)
    return result

def send(server, local_path=None, remote_path=None, user='root'):
    if not server:
        return
    target = server.accessIPv4
    ssh.send(target, local_path=local_path, remote_path=remote_path, user=user, keyfile=private_key)

def ping(server):
    if not server:
        return
    name = server.name
    target = server.accessIPv4
    command = 'ping -c 1 {} 2>&1 | grep "bytes from"'.format(target)
    limit = time.time() + config.timeout
    try:
        while time.time() < limit:
            (status, result) = commands.getstatusoutput(command)
            if result and len(result) > 0:
                log.debug(result)
                unreachable = re.compile('.*Destination Host Unreachable').match(result)
                ping_time = re.compile('.*time=(\d+(\.\d+)?) ms').match(result)
                if unreachable:
                    log.warn('Ping failed {}: {}'.format(target, unreachable.group(0)))
                else:
                    return True
            else:
                log.debug('No result from ping'.format(command))
            time.sleep(1)
        log.warning('Timed out waiting for server {} to become pingable'.format(server.id))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

def public_key_file():
    if not os.path.isfile(private_key):
        commands.getoutput("ssh-keygen -t rsa -P '' -N '' -f {}".format(private_key))
    return content(public_key)

def content(path):
    with open(path, 'r') as f:
        s = f.read()
    return s

# Based on https://github.com/openstack-infra/devstack-gate

def main():
    args = args_parser.parse_args()
    try:
        if args.reset:
            reset()
        server = setup()
        if not args.devstack_only:
            config_stack_vm(server)
        config_devstack_zuul_target(server)
        vm_devstack(server)
    except KeyboardInterrupt as ex:
        print "\nInterrupted"

if __name__ == '__main__':
    main()

