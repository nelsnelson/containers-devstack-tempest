#! /usr/bin/env bash

# Upgrade the server, install git, set up a "jenkins" account, 
# add user "jenkins" to sudoers, install pip packages, add tox via pip 
# (because the packaged version is too old) and reboot to make sure you're 
# running a current kernel:

# Upgrade the server
apt-get update --fix-missing
export DEBIAN_FRONTEND=noninteractive
echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections
apt-get upgrade -o Dpkg::Options::="--force-confnew" --assume-yes --fix-missing

# Install git
apt-get install --assume-yes --fix-missing git

# Clone the containers-devstack-tempest repo to get the
# rest of the installation scripts
git clone https://github.com/nelsnelson/containers-devstack-tempest.git /tmp/a

# Set up a "jenkins" account and add user "jenkins" to sudoers
/tmp/a/scripts/jenkins-user.sh

# Install pip packages, add tox via pip (because the
# packaged version is too old)
/tmp/a/scripts/openstack-infra-install.sh

