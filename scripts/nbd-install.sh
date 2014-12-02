#! /usr/bin/env bash

echo 'nbd' | tee -a /etc/modules
modprobe nbd
lsmod | grep -q nbd
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "The nbd module was installed"
else
    echo "The nbd module was not installed"
fi
