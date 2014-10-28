#! /usr/bin/env python

import sys

import get

def ip_address(id):
    server = get.server(id)
    print server.accessIPv4
    print server.addresses['private'][0]['addr']

def main():
    if len(sys.argv) < 2:
        print 'Please provide a server id'
        sys.exit(0)
    for arg in sys.argv[1:]:
        ip_address(arg)

if __name__ == '__main__':
    main()

