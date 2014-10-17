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

def until_up(host, timeout=config.timeout):
    if not host:
        return
    log.info('Waiting until server {} is up'.format(host.id))
    limit = time.time() + timeout
    try:
        while time.time() < limit:
            time.sleep(1)
            try:
                result = ssh.remote_exec(host.accessIPv4, host.adminPass, 'uptime')
            except Exception as ex:
                continue
        log.warning('Timed out waiting for server {} to boot up'.format(host.id))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

    return False

def remote_exec(host, command, timeout=config.timeout):
    if not host:
        return
    result = None
    limit = time.time() + timeout
    try:
        while time.time() < limit:
            time.sleep(0.5)
            result = ssh.remote_exec(host.accessIPv4, host.adminPass, command)
            if len(result) > 0:
                return result
        log.warning('Timed out waiting for server {} to respond'.format(host.id))
    except KeyboardInterrupt as ex:
        print "\nInterrupted"
        sys.exit(0)

    return False

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

