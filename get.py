#! /usr/bin/env python

import sys

import novaclient

import client
import logs

log = logs.logger('Get')

def server(id):
    try:
        log.info('Getting server with id {}'.format(id))
        server = client.nova.servers.get(id)
    except novaclient.openstack.common.apiclient.exceptions.NotFound as ex:
        log.error('No server with id {}'.format(id))
        sys.exit(1)
    return server

def main():
    if len(sys.argv) < 2:
        print "Please provide a server id"
        sys.exit(0)
    id = sys.argv[1]
    s = server(id)
    print '{}\t{}\t{}\t{}'.format(s.id, s.name, s.status, s.accessIPv4)

if __name__ == '__main__':
    main()

