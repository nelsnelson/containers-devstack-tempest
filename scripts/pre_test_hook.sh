#! /usr/bin/env bash

pre_test_hook() {
    mkdir -p /opt/stack/new
    rm -rf /opt/stack/new/devstack-gate
    git clone https://github.com/nelsnelson/devstack-gate /opt/stack/new/devstack-gate
}

export -f pre_test_hook
