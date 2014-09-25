#! /usr/bin/env python

import sys
import time

import client
import config
import logs
import wait

log = logs.logger('Create')

hints = { '0z0ne_target_host' : config.target_compute } if config.target_compute else None

def create(name, image=config.image, flavor=config.flavor, key_name=None, meta={}, files={}, timeout=config.timeout):
    image = client.nova.images.get(image)
    flavor = client.nova.flavors.get(flavor)
    if hints:
        log.info('Using compute host: {}'.format(hints.values()[0]))
    log.info('Creating server {} with {} flavor'.format(name, flavor.id))
    server = client.nova.servers.create(name, image, flavor, key_name=key_name, meta=meta, files=files, scheduler_hints=hints)
    log.info('Created server {} with password {}'.format(server.id, server.adminPass))
    if wait.has_state(server, 'ACTIVE', timeout):
        info = 'Server has started'
        if server.accessIPv4 or server.addresses['private'][0]['addr']:
            info += ' with '
        if server.accessIPv4:
            info += 'public-net IP {}'.format(server.accessIPv4)
        if server.accessIPv4 and server.addresses['private'][0]['addr']:
            info += ' and '
        if server.addresses['private'][0]['addr']:
            info += 'service-net IP {}'.format(server.addresses['private'][0]['addr'])
        log.info(info)
    return server

def main():
    if len(sys.argv) < 2:
        server_name = '{}-test-{}'.format(config.user, time.time())
    else:
        server_name = sys.argv[1]

    server = create(server_name)

if __name__ == '__main__':
    main()

