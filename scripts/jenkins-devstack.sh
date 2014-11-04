#! /usr/bin/env bash

PATH_OF_THIS_SCRIPT=`dirname "${0}"`
SCRIPT_DIR=${PATH_OF_THIS_SCRIPT/".\/"/"$(pwd)\/"}

source $SCRIPT_DIR/jenkins-devstack-env.sh

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
export NTP_SERVER=pool.ntp.org
rm $HOME/devstack-gate-log.txt
mkdir -p $WORKSPACE/tmp
`$WORKSPACE/safe-devstack-vm-gate-wrap.sh > $WORKSPACE/tmp/devstack-gate-log.txt` &
wait ${!}
mv $WORKSPACE/tmp/devstack-gate-log.txt $WORKSPACE/devstack-gate-log.txt
rmdir $WORKSPACE/tmp
