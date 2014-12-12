#! /usr/bin/env bash

pre_test_hook() {
    echo "Invoked pre_test_hook"
    mkdir -p /opt/stack/new
    rm -rf /opt/stack/new/devstack-gate
    echo "Cloning https://github.com/nelsnelson/devstack-gate into /opt/stack/new/devstack-gate"
    git clone https://github.com/nelsnelson/devstack-gate /opt/stack/new/devstack-gate

    sed -i 's/\#suspend\=true/#suspend=true\nsuspend=false/' /opt/stack/new/tempest/etc/tempest.conf
    sed -i 's/\#rescue\=true/#rescue=true\nrescue=false/' /opt/stack/new/tempest/etc/tempest.conf
    sed -i 's/\#resize\=false/#resize=false\nresize=false/' /opt/stack/new/tempest/etc/tempest.conf
    sed -i 's/\#xml_api_v2\=true/#xml_api_v2=true\nxml_api_v2=false/' /opt/stack/new/tempest/etc/tempest.conf
    sed -i 's/allow_tenant_isolation = True/allow_tenant_isolation = False/' /opt/stack/new/tempest/etc/tempest.conf

    LNUM=`grep -n '\[network-feature-enabled\]\napi_extensions' tempest.conf | cut -d':' -f1`

    sed -i "[network-feature-enabled]\napi_extensions = l3_agent_scheduler,agent,dhcp_agent_scheduler,router,allowed-address-pairs,extra_dhcp_opt/" "$(($LNUM))i" /opt/stack/new/tempest/etc/tempest.conf
    sed -i 's/[network-feature-enabled]\napi_extensions = all/api_extensions = l3_agent_scheduler,agent,dhcp_agent_scheduler,router,allowed-address-pairs,extra_dhcp_opt/' /opt/stack/new/tempest/etc/tempest.conf

    sed -i 's/ force_tenant_isolation = True/# force_tenant_isolation = True/' /opt/stack/new/tempest/tempest/api/compute/servers/test_list_servers_negative.py

}

export -f pre_test_hook
