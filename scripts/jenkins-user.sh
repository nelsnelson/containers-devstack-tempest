#! /usr/bin/env bash

adduser --quiet --disabled-password --gecos '' jenkins
mkdir -p /etc/sudoers.d
echo "jenkins ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/admin
#mkdir -p /home/jenkins/.ssh
#cp /root/.ssh/authorized_keys /home/jenkins/.ssh/
#chown -R jenkins: /home/jenkins/.ssh
#mkdir -p /home/jenkins/scripts
#mv /root/scripts/jenkins-devstack-env.sh /home/jenkins/scripts/jenkins-devstack-env.sh
#mv /root/scripts/jenkins-devstack.sh /home/jenkins/scripts/jenkins-devstack.sh
#chown -R jenkins: /home/jenkins/scripts

