#! /usr/bin/env python

import logging
import os
import socket
import sys

import paramiko

import logs

default_config = '~/.ssh/config'
session = {}

logging.getLogger('paramiko.transport').setLevel(logging.WARNING)
paramiko.util.log_to_file('/tmp/paramiko-ssh.log')

log = logs.logger('SSH')

def initialize_ssh_config(config):
    conf = paramiko.SSHConfig()
    path = os.path.expanduser(config)
    try:
        with open(path) as fd:
            conf.parse(fd)
    except IOError:
        log.error('Unable to load SSH config file {}'.format(path))
        return None
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
    proxy_command = conf.get('proxycommand', None) if conf else None
    return paramiko.ProxyCommand(proxy_command) if proxy_command else None

def initialize_client(host, port, password, user='root', config=None, key_file=None):
    try:
        log.info('Connecting to {}@{}:{} with password {}'.format(user, host, port, password))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key_file:
            c.connect(host, port=port, username=user, key_filename=key_file, sock=get_gateway(host, config=config))
        else:
            c.connect(host, port=port, username=user, password=password, sock=get_gateway(host, config=config))
    except socket.error as e:
        log.error('Low level socket error connecting to host %s: %s' % (host, e[1]))
        sys.exit(1)
    return c

def connect(host, port, password, user='root', config=None, key_file=None):
    key = '_client_{}'.format(host)
    if not key in session:
        session[key] = initialize_client(host, port, password, user=user, config=config, key_file=key_file)
    return session[key]

def remote_exec(address, user='root', password=None, command=None, config=None, key_file=None, port=22, quiet=False):
    if not (password and command):
        return
    try:
        ssh = connect(address, port, password, user=user, config=config, key_file=key_file)
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

