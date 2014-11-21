#! /usr/bin/env bash

if [ "${DEVSTACK_GATE_LIBVIRT_TYPE}" == "lxc" ]; then
    echo 'nbd' | tee -a /etc/modules
    modprobe nbd
    if [ $(lsmod | grep -q nbd) ]; then
        echo "Installed modprobe"
    fi
fi
