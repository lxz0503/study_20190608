#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

'UDP'

import re
import util
import subprocess
import pexpect
import socket
import time
import threading
from util import IF
import time

#common routines 
class RohcException(Exception):
    pass

class rohc_base:
    def __init__(self, host):
	self.host = host
 
    def rohc_exit(self):
	self.send('\r\n')
	self.send("exit\r\n")
	return True
	    
        # set rohc environment variable
    def rohc_env_set(self, var, value):
	self.host.set_sysvar(var, value)
        
    def rohc_shell_start(self):
        self.rohc_prompt = 'rohc>'    
        self.shell = "rohc" 
	self.prompt_org = self.host.s.prompt
	self.host.send(self.shell)

	self.host.s.prompt = self.rohc_prompt
	self.host.wait_prompt()
	time.sleep(1)

    def rohc_shell_exit(self):
	# exit rohc shell    
	self.host.send('exit')
	    
	# restore old prompt
	self.host.s.prompt = self.prompt_org
	self.host.wait_prompt()

    def rohc_close(self):
	lstop = self.host.send_and_return_all('close')
	time.sleep(2)

	for line in lstop:
	    m = re.match('(ROHC is closed)|(Failed to close ROHC)', line)
	    if m:
		break
	    else:
		raise RohcException('Rohc can not be closed')

    def rohc_open(self):
	lstart = self.host.send_and_return_all('open')
	time.sleep(2)
	for line in lstart:
	    m = re.match('(ROHC is opened)|(Failed to open ROHC, ret -1)', line)
 	    if m:
	        break
	    else:
		raise RohcException('Diameter client daemon can not be started')

#	def rohc_node_show(self):

    def rohc_configure(self, interface_name, interface_num, interface, profile, cid_val):
#       self.rohc_prompt = 'rohc>'
	self.rohc_shell_start()
#	self.rohc_close()
	self.rohc_open()
	lines = self.host.send_and_return_all('ifadd -ifname %s -ifnum %s' %(interface_name, interface_num))
        lines = self.host.send_and_return_all('ifprofileadd -ifname %s -profileid %s;' %(interface, profile))
	lines = self.host.send_and_return_all('compcidmod -ifname %s -profileid %s -cid %s;' %(interface, profile, cid_val))

    def rohc_cleanup(self):
        self.rohc_close()
        self.rohc_shell_exit()

#class  test_udp:
#    'Test UDP profile'
#    def config(self):
#        self.hosts = 3
#        self.eta = 15
#    def test(self, log, hosts, v6, _):
#	log('Rohc test', echo=True)
#	host1 = hosts[1]
#	host2 = hosts[2]
#       dut1  = hosts[1].ipcom_shell()   
#       dut2  = hosts[2].ipcom_shell() 
#       cid_type   = [ 'Large_cid']
#	cid_type   = ['Small_cid', 'Large_cid_0', 'Large_cid']
#               
#        for cid in cid_type: 
# Configure ROHC on targets peer1 and peer2   
#	    peer1 = rohc_base(host1) 
#	    peer2 = rohc_base(host2) 
#
# Small_cid: 
#            if cid == 'Small_cid':
#		dut1.set_sysvar('iprohc.large_cid', '0')
#		dut2.set_sysvar('iprohc.large_cid', '0')
#
# Large_cid_0 && Large_cid:
#            else: 
#                dut1.set_sysvar('iprohc.large_cid', '1')
#                dut2.set_sysvar('iprohc.large_cid', '1')
#                dut1.set_sysvar('iprohc.max_cid', '5000')
#                dut2.set_sysvar('iprohc.max_cid', '5000')
#
# Large_cid:
#            if cid == 'Large_cid':
#		peer1.rohc_configure('eth', '0', 'eth0', '2', '2000')
#                peer2.rohc_configure('eth', '0', 'eth0', '2', '2000')
#		peer1.rohc_shell_exit()
#		peer2.rohc_shell_exit()
#            else: 
#		peer1.rohc_configure('eth', '0', 'eth0', '2', '2')
#                peer2.rohc_configure('eth', '0', 'eth0', '2', '2')
#		peer1.rohc_shell_exit()    
#		peer2.rohc_shell_exit()   
#
# Begin testing  
#            dut1.echoserver(dut1.ip(),proto='udp')
#            dut2.echoserver(dut2.ip(),proto='udp')
#
# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions      
#            dut1.echoclient(dut2.ip(), proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)
#            dut2.echoclient(dut1.ip(), proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)
#
# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
#            dut1.echoclient(dut2.ip(), proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
#            dut2.echoclient(dut1.ip(), proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
#
# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
# Large_cid: Run this testing for large CID only to reduce the run time of this test case.  
#	    if cid == 'Large_cid':
#		dut1.echoclient(dut2.ip(), proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#		dut2.echoclient(dut1.ip(), proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#
# Test 2 connections with the same destination port
#            dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
#            dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True)
#            dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
#            dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True)
#
# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
#            dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
#            dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
#            dut1.stop_echoserver()
#            dut2.stop_echoserver()
#            dut1.echoserver(dut1.ip(), proto='udp', port = 7307)
#            dut2.echoserver(dut2.ip() ,proto='udp', port = 7307)
#            dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True)
#            dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True)
#
# Cleanup the testing 
#            dut1.stop_echoserver()
#            dut2.stop_echoserver()           
#
# Clean up the ROHC  
#            peer1.rohc_shell_start()
#            peer1.rohc_close()
#            peer1.rohc_shell_exit()                 
#            peer2.rohc_shell_start()
#            peer2.rohc_close()
#            peer2.rohc_shell_exit()

class small_cid:
    'Test UDP profile with small CID'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
	log('Rohc test: small_cid', echo=True)
	host1 = hosts[1]
	host2 = hosts[2]
        dut1  = hosts[1].ipcom_shell()   
        dut2  = hosts[2].ipcom_shell() 
        
# Configure ROHC on targets peer1 and peer2   
	peer1 = rohc_base(host1) 
	peer2 = rohc_base(host2) 

        dut1.set_sysvar('iprohc.large_cid', '0')
        dut2.set_sysvar('iprohc.large_cid', '0')

	peer1.rohc_configure('eth', '0', 'eth0', '2', '2')
	peer1.rohc_shell_exit()    
	peer2.rohc_configure('eth', '0', 'eth0', '2', '2')
	peer2.rohc_shell_exit()   

# Begin testing  
        dut1.echoserver(dut1.ip(),proto='udp')
        dut2.echoserver(dut2.ip(),proto='udp')

# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions     
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)


# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound 
# Between ports 7302/7301 in both directions
#	dut1.echoclient(dut2.ip(), proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Test 2 connections with the same destination port
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(dut1.ip(), proto='udp', port = 7307)
        dut2.echoserver(dut2.ip() ,proto='udp', port = 7307)
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True)

# Clean up 
        dut1.stop_echoserver()
        dut2.stop_echoserver()           

# Clean up the ROHC  
        peer1.rohc_shell_start()
#        peer1.rohc_close()
        peer1.rohc_shell_exit()                 
        peer2.rohc_shell_start()
#        peer2.rohc_close()
        peer2.rohc_shell_exit()

class large_cid:
    'Test UDP profile with large CID and large CID value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc test: large_cid', echo=True)
        host1 = hosts[1]
        host2 = hosts[2]
        dut1  = hosts[1].ipcom_shell()
        dut2  = hosts[2].ipcom_shell()

# Configure ROHC on targets peer1 and peer2
        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

# Small CID
        dut1.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '5000')
        dut2.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.max_cid', '5000')

        peer1.rohc_configure('eth', '0', 'eth0', '2', '2000')
        peer1.rohc_shell_exit()
        peer2.rohc_configure('eth', '0', 'eth0', '2', '2000')
        peer2.rohc_shell_exit()

# Begin testing
        dut1.echoserver(dut1.ip(),proto='udp')
        dut2.echoserver(dut2.ip(),proto='udp')

# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)


# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Test 2 connections with the same destination port
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(dut1.ip(), proto='udp', port = 7307)
        dut2.echoserver(dut2.ip() ,proto='udp', port = 7307)
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True)

# Clean up
        dut1.stop_echoserver()
        dut2.stop_echoserver()

# Clean up the ROHC
        peer1.rohc_shell_start()
#        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
#        peer2.rohc_close()
        peer2.rohc_shell_exit()

class large_cid_small_val:
    'Test UDP profile with large CID and small value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc test: large_cid_small_val', echo=True)
        host1 = hosts[1]
        host2 = hosts[2]
        dut1  = hosts[1].ipcom_shell()
        dut2  = hosts[2].ipcom_shell()

# Configure ROHC on targets peer1 and peer2
        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

        dut1.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '50')
        dut2.set_sysvar('iprohc.max_cid', '50')

        peer1.rohc_configure('eth', '0', 'eth0', '2', '2')
        peer1.rohc_shell_exit()
        peer2.rohc_configure('eth', '0', 'eth0', '2', '2')
        peer2.rohc_shell_exit()

# Begin testing
        dut1.echoserver(dut1.ip(),proto='udp')
        dut2.echoserver(dut2.ip(),proto='udp')

# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)


# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Test 2 connections with the same destination port
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(dut1.ip(), proto='udp', port = 7307)
        dut2.echoserver(dut2.ip() ,proto='udp', port = 7307)
        dut1.echoclient(dut2.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True)
        dut2.echoclient(dut1.ip(), proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True)

# Clean up
        dut1.stop_echoserver()
        dut2.stop_echoserver()

# Clean up the ROHC
        peer1.rohc_shell_start()
#        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
#        peer2.rohc_close()
        peer2.rohc_shell_exit()









