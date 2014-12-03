#! /usr/bin/env bash

PATH_OF_THIS_SCRIPT=`dirname "${0}"`
SCRIPT_DIR=${PATH_OF_THIS_SCRIPT/".\/"/"$(pwd)\/"}

if [ -f $SCRIPT_DIR/jenkins-devstack-env.sh ]; then
    source $SCRIPT_DIR/jenkins-devstack-env.sh
fi

if [ -f $SCRIPT_DIR/jenkins-devstack-env-overrides.sh ]; then
    source $SCRIPT_DIR/jenkins-devstack-env-overrides.sh
fi

if [ -f $SCRIPT_DIR/pre_test_hook.sh ]; then
    source $SCRIPT_DIR/pre_test_hook.sh
    export SKIP_DEVSTACK_GATE_PROJECT=1
fi

sudo DEBIAN_FRONTEND=noninteractive apt-get \
    --option "Dpkg::Options::=--force-confold" \
    --assume-yes install build-essential python-dev \
    python-software-properties linux-headers-virtual linux-headers-`uname -r`

mkdir -p $WORKSPACE
git clone $REPO_URL/$ZUUL_PROJECT $ZUUL_URL/$ZUUL_PROJECT
pushd $ZUUL_URL/$ZUUL_PROJECT
git checkout remotes/origin/$ZUUL_BRANCH
popd
pushd $WORKSPACE
git clone --depth 1 $REPO_URL/openstack-infra/devstack-gate
popd
cp $WORKSPACE/devstack-gate/devstack-vm-gate-wrap.sh $WORKSPACE/safe-devstack-vm-gate-wrap.sh
if [ -f $HOME/devstack-gate-log.txt ]; then
    rm $HOME/devstack-gate-log.txt
fi
mkdir -p $HOME/cache/files/
export DEBIAN_FRONTEND=noninteractive
nohup $WORKSPACE/safe-devstack-vm-gate-wrap.sh >$HOME/devstack-gate-log.txt 2>&1 &
wait ${!}
return_code=$?
echo "${return_code}" > /tmp/gate-finished

