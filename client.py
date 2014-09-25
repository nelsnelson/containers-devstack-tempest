
import novaclient.v1_1
import rackspace_auth_openstack.plugin

import config

bypass_url = None
auth_plugin = None

if config.bypass_url:
    bypass_url = config.bypass_url % config.tenant
if config.use_auth_plugin:
    auth_plugin = rackspace_auth_openstack.plugin.RackspaceAuthPlugin()

def nova_client():
    return novaclient.v1_1.Client(config.user, config.credential,
                                  config.tenant, config.auth_url,
                                  region_name=config.region,
                                  bypass_url=bypass_url,
                                  auth_system=config.auth_system,
                                  auth_plugin=auth_plugin,
                                  insecure=config.insecure)

try:
    if not nova:
        nova = nova_client()
except NameError:
    nova = nova_client()

