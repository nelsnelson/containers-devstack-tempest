#! /usr/bin/env python

import ssh

import novaclient

import client
import logs
import sys

log = logs.logger('SFTP')

private_key = './id_rsa'

def sftp(server, remote_path, user='root'):
    target = server.accessIPv4
    result = ssh.get(target, remote_path, user=user, keyfile=private_key)
    print result

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
        print 'Please provide a remote file to access'
        sys.exit(0)
    if len(sys.argv) < 1:
        print 'Please provide a host id'
        sys.exit(0)

    id = sys.argv[1]
    file = sys.argv[2]
    server = server(id)
    sftp(server, file)

if __name__ == '__main__':
    main()

