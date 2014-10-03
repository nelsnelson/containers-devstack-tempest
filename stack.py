#! /usr/bin/env python

import logging
import argparse
import commands
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

meta = dict()
image = None
flavor = None
private_key = './id_rsa'
public_key = './id_rsa.pub'
name_prefix = 'devstack-tempest'

def stack_vm():
    #fetch_public_key_file()
    #keypairs = client.nova.keypairs.list()
    #if find(lambda keypair: keypair.id == 'root', keypairs):
    #    keypairs.delete('root')
    #keypairs.create('root', key)
    fetch_image()
    fetch_flavor()
    server = None
    name = '{}-{}'.format(name_prefix, time.time())
    try:
        files = {
            '/root/.ssh/authorized_keys': public_key_file(),
            '/tmp/bootstrap.sh': content('scripts/bootstrap.sh')
        }
        server = create(name, files=files)
        time.sleep(4)
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
    remote(server, command='chmod +x /tmp/bootstrap.sh')
    remote(server, command='nohup /tmp/bootstrap.sh 2>&1')

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
    config_stack_vm(server)

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

def create(name, key_name=None, files=dict(), clock=True):
    log.info('Creating server {}'.format(name))
    server = client.nova.servers.create(name, image, flavor, key_name=key_name, meta=meta, files=files)
    log.info('Created server {} with password {}'.format(server.id, server.adminPass))
    if wait.has_state(server, 'ACTIVE', config.timeout):
        log.info('Server has started with IP address {}'.format(server.accessIPv4 or server.addresses['private'][0]['addr']))
    return server
 
def remote(server, user='root', command=config.command, clock=True):
    if not server:
        return
    name = server.name
    target = server.accessIPv4
    result = ssh.remote_exec(target, user=user, keyfile=private_key, command=command)
    if result:
        log.info(result)
    return result

def ping(server, clock=True):
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
                log.debug('No result from ping'.format(command))
            time.sleep(1)
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
        setup()
    except KeyboardInterrupt as ex:
        print "\nInterrupted"

if __name__ == '__main__':
    main()

