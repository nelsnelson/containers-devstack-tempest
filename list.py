#! /usr/bin/env python

import client

servers = client.nova.servers.list()

for server in servers:
    print '{}\t{}\t{}'.format(server.id, server.name, server.status)

