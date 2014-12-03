#! /usr/bin/env bash

export REPO_URL=https://review.openstack.org/p
export WORKSPACE=/home/jenkins/workspace/testing
export ZUUL_URL=http://github.com
export ZUUL_REF=HEAD
export ZUUL_PROJECT=openstack/nova
export ZUUL_BRANCH=master
export PYTHONUNBUFFERED=true
export DEVSTACK_GATE_TIMEOUT=120
export DEVSTACK_GATE_TEMPEST=1
export DEVSTACK_GATE_TEMPEST_FULL=1
export RE_EXEC=true

