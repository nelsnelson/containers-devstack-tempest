#! /usr/bin/env bash

exec > >(tee /tmp/bootstrap.log.txt)
exec 2>&1
# Upgrade the server, install git, update the system clock, set up a
# "jenkins" account, add user "jenkins" to sudoers, install pip packages,
# add tox via pip (because the packaged version is too old) and reboot to
# make sure you're running a current kernel:
apt-get update --fix-missing
export DEBIAN_FRONTEND=noninteractive
echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections
apt-get upgrade -o Dpkg::Options::="--force-confnew" --assume-yes --fix-missing
apt-get install --assume-yes --fix-missing git screen
git clone https://github.com/nelsnelson/containers-devstack-tempest.git /tmp/a
/tmp/a/scripts/jenkins-user.sh
/tmp/a/scripts/openstack-infra-install.sh

