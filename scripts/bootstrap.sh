#! /usr/bin/env bash

apt-get update --fix-missing
export DEBIAN_FRONTEND=noninteractive
echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections
apt-get upgrade -o Dpkg::Options::="--force-confnew" --assume-yes --fix-missing
apt-get install --assume-yes --fix-missing git
pushd /tmp
git clone git@github.rackspace.com:team-containers/containers-devstack-tempest/scripts
/tmp/scripts/jenkins-user.sh
cp /tmp/scripts/jenkins-devstack-env.sh /home/jenkins/scripts
cp /tmp/scripts/jenkins-devstack.sh /home/jenkins/scripts
/tmp/scripts/openstack-infra-install.sh

