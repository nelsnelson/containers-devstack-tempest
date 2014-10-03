#! /usr/bin/env bash

source ./jenkins-devstack-env.sh

mkdir -p $WORKSPACE
git clone $REPO_URL/$ZUUL_PROJECT $ZUUL_URL/$ZUUL_PROJECT
pushd $ZUUL_URL/$ZUUL_PROJECT
git checkout remotes/origin/$ZUUL_BRANCH
popd
pushd $WORKSPACE
git clone --depth 1 $REPO_URL/openstack-infra/devstack-gate
popd
cp $WORKSPACE/devstack-gate/devstack-vm-gate-wrap.sh $WORKSPACE/safe-devstack-vm-gate-wrap.sh
$WORKSPACE/safe-devstack-vm-gate-wrap.sh
