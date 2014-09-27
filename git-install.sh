#! /usr/bin/env bash

mkdir -p $HOME/src
pushd $HOME/src
git clone https://review.openstack.org/p/openstack-infra/config
config/install_puppet.sh && config/install_modules.sh
puppet apply --modulepath=/root/config/modules:/etc/puppet/modules -e \
"class { openstack_project::single_use_slave: install_users => false, ssh_key => \"$( cat $HOME/.ssh/id_rsa.pub | awk '{print $2}' )\" }"
popd

