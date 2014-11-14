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
    echo "Sourcing $SCRIPT_DIR/pre_test_hook.sh"
    source $SCRIPT_DIR/pre_test_hook.sh
    export SKIP_DEVSTACK_GATE_PROJECT=1
else
    echo "Not sourcing $SCRIPT_DIR/pre_test_hook.sh"
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
export DEBIAN_FRONTEND=noninteractive
echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections
apt-get install --assume-yes --fix-missing ntp
echo "server pool.ntp.org" > /etc/ntp.conf
export NTP_SERVER=pool.ntp.org
rm $HOME/devstack-gate-log.txt
mkdir -p $HOME/cache/files/
nohup $WORKSPACE/safe-devstack-vm-gate-wrap.sh >$HOME/devstack-gate-log.txt 2>&1 &
wait ${!}
return_code=$?
echo "${return_code}" > /tmp/gate-finished

