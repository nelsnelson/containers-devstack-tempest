#! /usr/bin/env bash

# Upgrade the server, install git, set up a "jenkins" account, 
# add user "jenkins" to sudoers, install pip packages, add tox via pip 
# (because the packaged version is too old) and reboot to make sure you're 
# running a current kernel:
apt-get update --fix-missing
export DEBIAN_FRONTEND=noninteractive
echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections
apt-get upgrade -o Dpkg::Options::="--force-confnew" --assume-yes --fix-missing
apt-get install --assume-yes --fix-missing git
[[ -z `cat /etc/timezone | grep "America/Chicago"` ]] && (echo "America/Chicago" | tee /etc/timezone)
cat /etc/timezone
dpkg-reconfigure --frontend noninteractive tzdata
apt-get install --fix-missing --assume-yes ntpdate
ntpdate pool.ntp.org

git clone https://github.com/nelsnelson/containers-devstack-tempest.git /tmp/a
/tmp/a/scripts/jenkins-user.sh
/tmp/a/scripts/openstack-infra-install.sh

