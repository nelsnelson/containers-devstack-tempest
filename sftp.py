#! /usr/bin/env python

import sys

import get
import ssh

private_key = './id_rsa'

def main():
    if len(sys.argv) < 3:
        print 'Usage:', sys.argv[0], ' <server_id> <remote_path>'
        sys.exit(0)

    id = sys.argv[1]
    file = sys.argv[2]
    server = get.server(id)
    print ssh.fetch(server, file)

if __name__ == '__main__':
    main()

