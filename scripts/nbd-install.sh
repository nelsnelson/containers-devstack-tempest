#! /usr/bin/env bash

echo 'nbd' | tee -a /etc/modules
modprobe nbd
if [ $(lsmod | grep -q nbd) ]; then
    echo "Installed nbd"
else
    echo "Did not install nbd"
fi
