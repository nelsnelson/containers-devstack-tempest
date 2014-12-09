#! /usr/bin/env python

import sys
import time

import novaclient

import client
import config
import get
import logs
import ssh

log = logs.logger('Wait')

def wait(id, state):
    server = get.server(id)
    has_state(server, state)

def has_state(server, state, timeout=config.timeout, silently=False):
    if not server:
        return
    log.info('Waiting until server {} status is {}'.format(server.id, state))
    limit = time.time() + timeout
    try:
        while time.time() < limit:
            time.sleep(1)
            try:
                result = client.nova.servers.get(server.id)
                if not silently:
                    log.info('Server {} is in state {}'.format(server.id, result.status))
                if result.status == state:
                    return True
                elif result.status == 'ERROR':
                    raise Exception('Server state is ERROR')
            except novaclient.exceptions.NotFound as ex:
                log.info('No such server {}'.format(server.id))
                return False
        log.warning('Timed out waiting for server {} status {}'.format(server.id, state))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

    return False

def until_gone(server, timeout=config.timeout):
    if not server:
        return
    log.info('Waiting until server {} is gone'.format(server.id))
    limit = time.time() + timeout
    try:
        while time.time() < limit:
            time.sleep(1)
            servers = client.nova.servers.list()
            if find(lambda i: i.id == server.id, servers):
                continue
            else:
                return True
        log.warning('Timed out waiting for server {} to go away'.format(server.id))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

    return False

def until_up(host, timeout=config.timeout, interval=1, user='root', keyfile=None):
    if not host:
        return
    target = host.accessIPv4
    log.info('Waiting until host {} is up at {}'.format(host.id, target))
    limit = time.time() + timeout
    try:
        while time.time() < limit:
            time.sleep(interval)
            try:
                result = ssh.remote_exec(target, user=user, command='uptime', keyfile=keyfile, quiet=True)
                if result:
                    print result
                    log.warning('Host {} is up'.format(host.id))
                    return True
            except Exception as ex:
                log.warning('Host {} at {} is not up yet'.format(host.id, target))
                continue
        log.warning('Timed out waiting for host {} at {} to boot up'.format(host.id, target))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

    return False

def remote_exec(host, command, timeout=config.timeout):
    if not host:
        return
    target = host.accessIPv4
    result = None
    limit = time.time() + timeout
    try:
        while time.time() < limit:
            time.sleep(0.5)
            result = ssh.remote_exec(target, host.adminPass, command)
            if len(result) > 0:
                return result
        log.warning('Timed out waiting for host {} to respond'.format(target))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

    return False

def until_path_exists(host, path='/tmp', user='root', keyfile=None):
    target = host.accessIPv4
    log.info('Waiting until file path exists {}:{}...'.format(target, path))
    limit = time.time() + 30000
    try:
        while time.time() < limit:
            time.sleep(20)
            result = ''
            try:
                command = '[[ -f {} ]] && echo done'.format(path)
                result = ssh.remote_exec(target, user=user, keyfile=keyfile, command=command)
            except Exception as ex:
                log.error("Error waiting for file {}: {}".format(path, ex.message))
            if len(result) > 0:
                return
        log.warning('Timed out waiting for {}'.format(path))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item): 
            return item

def main():
    if len(sys.argv) < 3:
        print 'Please provide an id and a state for which to wait'
    id = sys.argv[1]
    state = sys.argv[2]
    wait(id, state)

if __name__ == '__main__':
    main()

