#! /usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive
echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections
apt-get upgrade -o Dpkg::Options::="--force-confnew" --assume-yes --fix-missing
apt-get install --assume-yes --fix-missing git

