#! /usr/bin/env bash

apt-get update --fix-missing
export DEBIAN_FRONTEND=noninteractive
echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections
apt-get upgrade -o Dpkg::Options::="--force-confnew" --assume-yes --fix-missing
apt-get install --assume-yes --fix-missing git
git clone https://github.com/nelsnelson/containers-devstack-tempest.git /tmp/a
/tmp/a/scripts/jenkins-user.sh
/tmp/a/scripts/openstack-infra-install.sh

