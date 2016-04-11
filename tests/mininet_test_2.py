#!/usr/bin/python
# This program measures number of flows a switch can support until it start software switching
#using mininet

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import Intf
from mininet.util import custom, pmonitor

import threading
import time
import math

# Specify interfaces that are connected to the target switch
interface1 = 'eth2'
interface2 = 'eth4'

def max_flow_test(max_flows,num_iperf = 1):
    n =  int(2*(math.sqrt(max_flows/2)))
    net = Mininet( topo=None,build=None)

    s2 = net.addSwitch('s2',failMode='standalone')
    s3 = net.addSwitch('s3',failMode='standalone')

    subnet1 = []
    subnet2 = []
    for i in range(1,n+1):
        if i <= n/2:
            host = net.addHost('h%s' % i, ip='10.0.0.%s' % i)
            net.addLink(host, s2)
            subnet1.append(host)
        else:
            host = net.addHost('h%s' % i, ip='10.0.1.%s' % i)
            net.addLink(host, s3)
            subnet2.append(host)

    print('%s nodes generated' %n)

    Intf( interface1, node=s2 )
    Intf( interface2, node=s3 )

    net.start()
    count = 0
    popens = {}
    for host1 in subnet1:
        for host2 in subnet2:
            popens[host1] = host1.popen( "ping %s" % host2.IP() )
            count += 1

    print('%s connections generated, %s flows generated ' %(count,count*2))
    time.sleep(3)

    iperf_outputs = {}

    for i in range(1,num_iperf+1):
        subnet1[-i].popen('iperf -s')
        time.sleep(1)
        iperf = subnet2[-i].popen('iperf -T20 -c ' + subnet1[-i].IP())
        iperf_outputs[subnet2[-i]] = iperf
        
    for host, line in pmonitor( iperf_outputs ):
        if host:
            print "<%s>: %s" % ( host.name, line.strip() )

    for host in subnet1:
        host.cmd('pkill ping')

    for host in subnet2:
        host.cmd('pkill ping')

    for i in range(1,num_iperf+1):
        subnet2[-i].cmd('pkill iperf')
    net.stop()

if __name__ == '__main__':
    #max_flow_test(112)
    #max_flow_test(128)
    max_flow_test(200,num_iperf = 1)
