#! /usr/bin/env bash

adduser --quiet --disabled-password --gecos '' jenkins
mkdir -p /etc/sudoers.d
echo "jenkins ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/admin

