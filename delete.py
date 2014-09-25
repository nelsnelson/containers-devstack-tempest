#! /usr/bin/env python

import sys

import novaclient

import get
import logs
import wait

log = logs.logger('Load')

def delete(id):
    server = get.server(id)
    if server.status == 'ACTIVE':
        log.info('Server {} is active'.format(server.id))
        stop(server)
    else:
        reset(server)

    log.info('Deleting server {}'.format(server.id))
    result = server.delete()

    if result:
        log.info('Result of delete for server {}: {}'.format(id, result.__class__))

def stop(server):
    try:
        log.info('Attempt to stop server {}'.format(server.id))
        server.stop()
    except novaclient.exceptions.Conflict as ex:
        log.error('Failed to delete server {}: {}'.format(server.id, ex.message))
    except novaclient.openstack.common.apiclient.exceptions.BadRequest as ex:
        if 'Cannot stop while the instance is in this state.' in ex.message:
            log.error(ex.message)
            reset(server)
            try:
                log.info('Second attempt to stop server {}'.format(server.id))
                server.stop()
            except novaclient.openstack.common.apiclient.exceptions.BadRequest as ex:
                log.error(ex.message)

def reset(server):
    log.info('Resetting state for server {}'.format(server.id))
    server.reset_state('active')
    if wait.has_state(server, 'ACTIVE'):
        log.info('State of server {} is {}'.format(server.id, server.status))

def main():
    if len(sys.argv) < 2:
        print 'Please provide a server id'
        sys.exit(0)
    for arg in sys.argv[1:]:
        delete(arg)

if __name__ == '__main__':
    main()

