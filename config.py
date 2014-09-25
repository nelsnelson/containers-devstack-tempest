
import ConfigParser
import os

Config = ConfigParser.ConfigParser()
Config.read('.config')
stanza = os.path.basename(os.getcwd())
if stanza == os.path.basename(os.path.dirname(os.path.realpath(__file__))):
    stanza = 'iad'
stanza = os.getenv('DATACENTER', stanza)

def string(key, default=''):
    try:
        v = Config.get(stanza, key)
    except ConfigParser.NoOptionError:
        v = default
    return v

def integer(key, default=0):
    try:
        v = Config.getint(stanza, key)
    except ConfigParser.NoOptionError:
        v = default
    return v

def boolean(key, default=False):
    try:
        v = Config.getboolean(stanza, key)
    except ConfigParser.NoOptionError:
        v = default
    return v

servers  = integer('servers', 1)
threads  = integer('threads', 30)
duration = integer('duration', 30)
timeout  = integer('timeout', 30)
command  = string('command', 'uptime')

user       = string('user')
credential = string('password') or string('token')
account    = string('account')
image      = string('image')
flavor     = string('flavor')
target_compute = string('target_compute', None)

region          = string('region')
tenant          = string('tenant') or string('account')
auth_url        = string('auth_url')
bypass_url      = string('bypass_url')
auth_system     = string('auth_system')
use_auth_plugin = string('use_auth_plugin')
insecure        = boolean('insecure', False)
tear_down       = boolean('tear_down', True)

