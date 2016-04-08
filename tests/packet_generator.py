"""Demonstrates how to construct and send raw Ethernet packets on the
network.

You probably need root privs to be able to bind to the network interface,
"""


from socket import *
import threading
import signal, os, sys, time, select
from datetime import datetime, timedelta

from ryu.ofproto import ether
from ryu.lib.packet import packet
import tester
import json
import inspect

# import all packet libraries.
PKT_LIB_PATH = 'ryu.lib.packet'
for modname, moddef in sys.modules.items():
    if not modname.startswith(PKT_LIB_PATH) or not moddef:
        continue
    for (clsname, clsdef, ) in inspect.getmembers(moddef):
        if not inspect.isclass(clsdef):
            continue
        exec('from %s import %s' % (modname, clsname))


# Make sure these interfaces are in promiscuous mode
snd_interface = 'eth4'
rcv_interface = 'eth5'
running = True
total_pkt_sent = 0

def receive(interface):
    counter = size = 0
    total_pkt = total_size = 0

    start_time = prev_time  = datetime.now()
    s = socket(AF_PACKET , SOCK_RAW , ntohs(0x0003))
    s.bind((interface, 0))

    while running:
        ready_to_read, ready_to_write, in_error = select.select([s],[],[],1)

        for s in ready_to_read:
            pkt = s.recv(1500)
            counter += 1
            size += len(pkt)

        curr_time = datetime.now()
        timediff = (curr_time-prev_time).total_seconds()
        if timediff > 1:
            pps = float(counter) /timediff 
            bps = float(size) / timediff
            print('duration %s, pps = %s, total = %s, bps = %s (%s Mb/s)' %(timediff,pps,total_pkt, bps, bps*8/1024/1024))
            total_pkt += counter
            total_size += size
            counter = size = 0
            prev_time = curr_time

    total_sec = (curr_time - start_time).total_seconds()
    print('%s total packets received, average bps = %s' % (total_pkt,total_size/total_sec))
    print('Finishing theads')

def sendeth(packet, pps = 1 , interface = "eth2"):
    interval_ms = (1000000.0/float(pps))
    packet.serialize()
    s = socket(AF_PACKET, SOCK_RAW)
    s.bind((interface, 0))
    global total_pkt_sent

    while running:
        """Send raw Ethernet packet on interface."""
        prev = datetime.now()
        nxt_pkt_time = datetime.now() + timedelta(microseconds=interval_ms)
        for num_pkt in range(0,pps):

            s.send(packet.data)
            total_pkt_sent += 1
            curr_pkt_time = datetime.now()
            if nxt_pkt_time > curr_pkt_time:
                timediff_ms = (nxt_pkt_time - curr_pkt_time).microseconds
                #print('nxt_pkt_time = %s , curr_time = %s, timediff = %s ' %(nxt_pkt_time, curr_pkt_time, timediff_ms))

                time.sleep(float(timediff_ms) / 1000000)
            nxt_pkt_time += timedelta(microseconds=interval_ms)
        print('%s packets sent, total = %s' % (pps, total_pkt_sent))
        curr = datetime.now()

if __name__ == "__main__":

    testfiles = tester.TestFile('01_DROP_00_KBPS_01_10M.json',None)
    for testfile  in testfiles.tests:
        test = testfile.tests[0]
        packet_text = test['packets']['packet_text']
        pkt = eval('/'.join(packet_text))

    recv_t = threading.Thread(target=receive, args=(rcv_interface,))
    recv_t.start()
    time.sleep(2)
    try:
        r = sendeth(pkt,interface=snd_interface,pps = 30000)
    except KeyboardInterrupt:
        print('interrupted')
        running = False
        print('%s total packet sent\n'%total_pkt_sent)
