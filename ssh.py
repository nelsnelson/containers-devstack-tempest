#! /usr/bin/env python

import logging
import os
import socket
import sys
import time

import paramiko

import logs

default_config = '~/.ssh/config'
session = {}

logging.getLogger('paramiko.transport').setLevel(logging.WARNING)
paramiko.util.log_to_file('/tmp/paramiko-ssh.log')

log = logs.logger('SSH')

def initialize_ssh_config(config):
    print 'wtf 1'
    if not os.path.isfile(config):
        return None
    print 'wtf 2'
    conf = paramiko.SSHConfig()
    print 'wtf 3'
    path = os.path.expanduser(config)
    print 'wtf 4'
    try:
        with open(path) as fd:
            conf.parse(fd)
    except IOError:
        log.error('Unable to load SSH config file {}'.format(path))
        return None
    print 'wtf 5'
    print 'conf: {}'.format(conf)
    return conf

def ssh_config(host, config=None):
    key = '_ssh_config_{}'.format(host)
    if not key in session:
        session[key] = initialize_ssh_config(config or default_config)
    return session[key].lookup(host) if session[key] else None

def get_gateway(host, config=None):
    if config:
        conf = ssh_config(host, config=config)
    conf = ssh_config(host)
    log.info('Getting gateway for {}'.format(conf))
    proxy_command = conf.get('proxycommand', None) if conf else None
    return paramiko.ProxyCommand(proxy_command) if proxy_command else None

def initialize_client(host, port, password=None, user='root', config=None, keyfile=None):
    while True:
        try:
            if keyfile:
                log.info('Connecting to {}@{}:{} with keyfile {}'.format(user, host, port, keyfile))
            elif password:
                log.info('Connecting to {}@{}:{} with password {}'.format(user, host, port, password))
            c = paramiko.SSHClient()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if keyfile:
                c.connect(host, port=port, username=user, key_filename=keyfile, sock=get_gateway(host, config=config))
            else:
                c.connect(host, port=port, username=user, password=password, sock=get_gateway(host, config=config))
            break
        except socket.error as e:
            log.error('Low level socket error connecting to host %s: %s' % (host, e[1]))
            if e[1] == 'Connection refused':
                log.warn('Attempting to reconnect...')
                time.sleep(10)
                continue
            else:
                sys.exit(1)
    return c

def is_connected(ssh):
    transport = ssh.get_transport() if ssh else None
    return transport and transport.is_active()

def connect(host, port, password=None, user='root', config=None, keyfile=None):
    key = '_client_{}@{}'.format(user, host)
    if key in session and is_connected(session[key]):
        return session[key]
    session[key] = initialize_client(host, port, password, user=user, config=config, keyfile=keyfile)
    return session[key]

def remote_exec(address, user='root', password=None, command=None, config=None, keyfile=None, port=22, quiet=False):
    if not ((password or keyfile) and command):
        return
    try:
        ssh = connect(address, port, password, user=user, config=config, keyfile=keyfile)
        if not quiet:
            log.info('Remote command to {}: {}'.format(address, command))
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.readlines()
        if output and len(output) > 0:
            return output[0].strip()
    except paramiko.ssh_exception.SSHException as ex:
        log.error('Remote execution error: {}'.format(ex.message))
        raise ex
    return ''

def main():
    if len(sys.argv) < 3:
        print 'Usage: ./ssh.py <ip-address> <password> <command> [ssh-config-file]'
        sys.exit(0)
    address = sys.argv[1]
    password = sys.argv[2]
    command = sys.argv[3]
    config = sys.argv[4] if len(sys.argv) > 4 else None
    print remote_exec(address, password, command, config)

if __name__ == '__main__':
    main()

