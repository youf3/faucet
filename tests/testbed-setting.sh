#!/bin/bash

#This script sets up ovs with four interfaces for ryu-testing framework

bridge="br0"
int1="eth2"
int2="eth4"
int3="eth5"
int4="eth6"

controller="tcp:127.0.0.1:6633"
dpid="0000000024cf8e6c"


ovs-vsctl add-br $bridge
ovs-vsctl add-port $bridge $int1
ovs-vsctl add-port $bridge $int2
ovs-vsctl add-port $bridge $int3
ovs-vsctl add-port $bridge $int4
ovs-vsctl set-fail-mode $bridge secure
ovs-vsctl set-controller $bridge $controller
ovs-vsctl set bridge $bridge protocols=OpenFlow13
ovs-vsctl set bridge $bridge other-config:datapath-id=$dpid
