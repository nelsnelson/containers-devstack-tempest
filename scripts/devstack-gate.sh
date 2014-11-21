export REPO_URL=https://review.openstack.org/p
export ZUUL_URL=/home/jenkins/workspace-cache
export ZUUL_REF=HEAD
export WORKSPACE=/home/jenkins/workspace/testing
export ZUUL_PROJECT=openstack/nova
export ZUUL_BRANCH=master
export PYTHONUNBUFFERED=true
export DEVSTACK_GATE_TIMEOUT=120
export DEVSTACK_GATE_TEMPEST=1
export DEVSTACK_GATE_TEMPEST_FULL=1
export DEVSTACK_GATE_LIBVIRT_TYPE=lxc
export DEVSTACK_GATE_TEMPEST_REGEX=tempest.api.compute.servers.test_servers.ServersTestJSON.test_create_server_with_admin_password
export RE_EXEC=true
mkdir -p $WORKSPACE
cp devstack-gate/devstack-vm-gate-wrap.sh ./safe-devstack-vm-gate-wrap.sh
./safe-devstack-vm-gate-wrap.sh
