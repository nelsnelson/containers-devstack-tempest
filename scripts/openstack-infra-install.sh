#! /usr/bin/env bash

mkdir -p /home/jenkins/src
pushd /home/jenkins/src
#git clone https://review.openstack.org/p/openstack-infra/config
git clone https://github.com/openstack-infra/system-config.git
#config/install_puppet.sh && config/install_modules.sh
system-config/install_puppet.sh && config/install_modules.sh
puppet apply --modulepath=/root/config/modules:/etc/puppet/modules -e \
"class { openstack_project::single_use_slave: install_users => false, ssh_key => \"$( cat $HOME/.ssh/id_rsa.pub | awk '{print $2}' )\" }"
popd

