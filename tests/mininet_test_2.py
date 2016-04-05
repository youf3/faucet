#!/usr/bin/python

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import Intf
from mininet.util import custom, pmonitor

import threading
import time
import math

def max_flow_test(max_flows):
    n =  int(2*(math.sqrt(max_flows/2)))
    print('%s nodes generated' %n)
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

    Intf( 'eth2', node=s2 )
    Intf( 'eth4', node=s3 )

    net.start()
    count = 0
    popens = {}
    for host1 in subnet1:
        for host2 in subnet2:
            popens[host1] = host1.popen( "ping %s" % host2.IP() )
            #print('ping %s -> %s' %(host1, host2))
            count += 1

    print('%s connections generated '%count)
    #for host, line in pmonitor( popens ):
        #if host:
            #print "<%s>: %s" % ( host.name, line.strip() )
            #subnet1[-1].cmd('ping ', subnet2[-1].IP())        
    time.sleep(10)
    net.iperf((subnet1[-1],subnet2[-1]),seconds=30)
    net.stop()

if __name__ == '__main__':
    #max_flow_test(112)
    #max_flow_test(128)
    max_flow_test(2)
