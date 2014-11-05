#! /usr/bin/env bash

export REPO_URL=https://review.openstack.org/p
#export ZUUL_URL=/home/jenkins/workspace-cache
export ZUUL_URL=http://github.com
export ZUUL_REF=HEAD
export WORKSPACE=/home/jenkins/workspace/testing
#export ZUUL_PROJECT=openstack/nova
export ZUUL_PROJECT=nelsnelson/devstack-gate
#export ZUUL_BRANCH=master
export ZUUL_BRANCH=libvirt_target
export PYTHONUNBUFFERED=true
export DEVSTACK_GATE_TIMEOUT=120
export DEVSTACK_GATE_TEMPEST=1
export DEVSTACK_GATE_TEMPEST_FULL=1
export RE_EXEC=true

