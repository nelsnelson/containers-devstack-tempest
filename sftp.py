#! /usr/bin/env python

import ssh

import novaclient

import get
import logs
import sys

log = logs.logger('SFTP')

private_key = './id_rsa'

def sftp(server, remote_path, user='root'):
    target = server.accessIPv4
    try:
        result = ssh.get(target, remote_path, user=user, keyfile=private_key)
        print result
    except IOError as ex:
        log.error("Error: {}".format(ex[1]))

def main():
    if len(sys.argv) < 3:
        print 'Usage:', sys.argv[0], ' <server_id> <remote_path>'
        sys.exit(0)

    id = sys.argv[1]
    file = sys.argv[2]
    server = get.server(id)
    sftp(server, file)

if __name__ == '__main__':
    main()

