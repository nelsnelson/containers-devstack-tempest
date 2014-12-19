#! /usr/bin/env bash

#export REPO_URL=https://review.openstack.org/p
export REPO_URL=https://git.openstack.org
export WORKSPACE=/home/jenkins/workspace/testing
export ZUUL_URL=http://github.com
export ZUUL_REF=HEAD
export ZUUL_PROJECT=openstack/nova
export ZUUL_BRANCH=master
export PYTHONUNBUFFERED=true
export DEVSTACK_GATE_TIMEOUT=120
export DEVSTACK_GATE_TEMPEST=1
export DEVSTACK_GATE_TEMPEST_FULL=1
export DEVSTACK_GATE_TEMPEST_DISABLE_TENANT_ISOLATION=true
export NETWORK_API_EXTENSIONS=l3_agent_scheduler,agent,dhcp_agent_scheduler,router,allowed-address-pairs,extra_dhcp_opt
export RE_EXEC=true

