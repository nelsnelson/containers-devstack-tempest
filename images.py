#! /usr/bin/env python

import client

for image in client.nova.images.list():
    print '{}\t{}'.format(image.id, image.name) 

