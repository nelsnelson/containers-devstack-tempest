#! /usr/bin/env python

import logging
import argparse
import commands
import random
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

meta = dict()
image = None
flavor = None
public_key = './id_rsa.pub'

def stack():
    server = None
    name = 'devstack-tempest-{}'.format(time.time())
    try:
        files = { '/root/.ssh/authorized_keys': public_key_file()}
        server = create(name, files=files)
        time.sleep(4)
        ping(server)
        log.info('Created server {}'.format(server.name))

# Upgrade the server, install git and pip packages, add tox via pip 
# (because the packaged version is too old), set up a "jenkins" account 
# (add user "jenkins" to sudoers) and reboot to make sure you're 
# running a current kernel:
        remote(server, """export DEBIAN_FRONTEND=noninteractive \\
&& echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections \\
&& apt-get upgrade -o Dpkg::Options::="--force-confnew" --assume-yes --fix-missing \\
&& apt-get install --assume-yes --fix-missing git \\
&& adduser --quiet --disabled-password --gecos '' jenkins \\
&& mkdir -p /etc/sudoers.d \\
&& echo "jenkins ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/admin \\
&& mkdir -p $HOME/src && pushd $HOME/src \\
&& git clone https://review.openstack.org/p/openstack-infra/config \\
&& config/install_puppet.sh && config/install_modules.sh \\
&& puppet apply --modulepath=/root/config/modules:/etc/puppet/modules \\
-e "class { openstack_project::single_use_slave: install_users => false,
ssh_key => \"$( cat $HOME/.ssh/id_rsa.pub | awk '{print $2}' )\" }" \\
&& reboot"""

    except KeyboardInterrupt as ex:
        print 'Interrupted'
        sys.exit(0)

def setup():
    fetch_image()
    fetch_flavor()
    #fetch_public_key_file()
    #for keypair in client.nova.keypairs.list():
    #    if keypair.id == 'debian':
    #        keypairs.delete('debian')
    #keypairs.create('debian', key)

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
 
def remote(server, command=config.command, clock=True):
    if not server:
        return
    name = server.name
    target = server.accessIPv4
    result = ssh.remote_exec(server, password=server.adminPass, command=command, timeout=config.timeout)
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
    commands.getoutput("ssh-keygen -t rsa -P '' -N '' -f ./id_rsa")
    return content(public_key)
 
def content(p):
    with open(p, 'r') as f:
        content = f.read()
    return content

def main():
    try:
        setup()
        stack()
    except KeyboardInterrupt as ex:
        print "\nInterrupted"

if __name__ == '__main__':
    main()

