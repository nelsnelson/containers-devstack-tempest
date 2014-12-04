#! /usr/bin/env bash

apt-get install --assume-yes --fix-missing ntp
echo "server pool.ntp.org" > /etc/ntp.conf
export NTP_SERVER=pool.ntp.org

git clone https://git.openstack.org/openstack-infra/system-config
system-config/install_puppet.sh && system-config/install_modules.sh
puppet apply --modulepath=/root/system-config/modules:/etc/puppet/modules -e \
"class { openstack_project::single_use_slave: install_users => false, ssh_key => \"$( cat $HOME/.ssh/id_rsa.pub | awk '{print $2}' )\" }"

