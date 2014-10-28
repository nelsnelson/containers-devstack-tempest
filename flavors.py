#! /usr/bin/env python

import re
import sys

import novaclient

import client
import logs

log = logs.logger('Flavor')

def list_flavors(query=None):
    flavors = list()
    if query:
        p = re.compile('.*{}.*'.format(query), re.I)
    for flavor in client.nova.flavors.list():
        if query and p.match(flavor.name):
            flavors.append(flavor)
    return sorted(flavors, key=lambda f: f.id)

def get(flavor_id):
    try:
        return client.nova.flavors.get(flavor_id)
    except novaclient.openstack.common.apiclient.exceptions.NotFound as ex:
        log.error('Failed to get flavor: {}'.format(ex.message))

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else None
    for flavor in list_flavors(query):
        print '{}\t{}'.format(flavor.id, flavor.name)

if __name__ == '__main__':
    main()
