#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


import re
import util
import subprocess
import pexpect
import socket
import time
import threading
import time
#import pdb
import string

from util import IF

from tunnel import _test_setup, _test_tunnel, _has_ipv6_support
from iprohc_common import config_pppoe, pppoe_addr, rohc_base, validate_and_cleanup_rohc, test_setup

def esp_config(peer1, peer2, addr1, addr2, v6):
#----------------------------------------------------------------------#
# Peer 1
#################### output ####################
#    keyadm add -new -enc aes -auth md5 -spi 603 -dst 147.11.217.131 -src 147.11.217.130 -ekey b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480 -akey 8317954752bf255b5321fe19e54a7f8d -ingress
#    keyadm addflow -spi 603 -dst 147.11.217.131 -proto esp -srcmask 255.255.255.255 -dstmask 255.255.255.255 -srcflow 147.11.217.130 -dstflow 147.11.217.131 -ingress"
#################### output  ####################
#    keyadm add -new -enc aes -auth md5 -spi 603 -dst 147.11.217.130 -src 147.11.217.131 -ekey b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480 -akey 8317954752bf255b5321fe19e54a7f8d
#    keyadm addflow -spi 603 -dst 147.11.217.130 -proto esp -srcmask 255.255.255.255 -dstmask 255.255.255.255 -srcflow 147.11.217.131 -dstflow 147.11.217.130

# Peer 2  
#################### input  ####################
#    keyadm add -new -enc aes -auth md5 -spi 603 -dst 147.11.217.130 -src 147.11.217.131 -ekey b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480 -akey 8317954752bf255b5321fe19e54a7f8d -ingress
#    keyadm addflow -spi 603 -dst 147.11.217.130 -proto esp -srcmask 255.255.255.255 -dstmask 255.255.255.255 -srcflow 147.11.217.131 -dstflow 147.11.217.130 -ingress
#################### output  ####################
#    keyadm add -new -enc aes -auth md5 -spi 603 -dst 147.11.217.131 -src 147.11.217.130 -ekey b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480 -akey 8317954752bf255b5321fe19e54a7f8d
#    keyadm addflow -spi 603 -dst 147.11.217.131 -proto esp -srcmask 255.255.255.255 -dstmask 255.255.255.255 -srcflow 147.11.217.130 -dstflow 147.11.217.131
#----------------------------------------------------------------------#

    if v6:
        srcmask = dstmask = "ffff:ffff:ffff:ffff::"
    else:
        srcmask = dstmask = "255.255.0.0"

#----------------------------------------------------------------------#
# Peer 1
#################### input ####################
    srcaddr = srcflow = addr1
    dstaddr = dstflow = addr2

    peer2.host.send_and_return_all( \
    'keyadm add -new -enc aes -auth md5 -spi 603 -dst %s -src %s -ekey \
    b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480 -akey 8317954752bf255b5321fe19e54a7f8d -ingress' \
    % (dstaddr, srcaddr)) 

    peer2.host.send_and_return_all( \
    'keyadm addflow -spi 603 -dst %s -proto esp -srcmask %s -dstmask %s -srcflow %s -dstflow %s -ingress' \
    % (dstaddr, srcmask, dstmask, srcflow, dstflow))

#################### output  ####################
    srcaddr = srcflow = addr2
    dstaddr = dstflow = addr1

    peer2.host.send_and_return_all( \
    'keyadm add -new -enc aes -auth md5 -spi 603 -dst %s -src %s \
    -ekey b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480 -akey 8317954752bf255b5321fe19e54a7f8d' \
    % (dstaddr, srcaddr))

    peer2.host.send_and_return_all( \
    'keyadm addflow -spi 603 -dst %s -proto esp -srcmask %s -dstmask %s -srcflow %s -dstflow %s' \
    % (dstaddr, srcmask, dstmask, srcflow, dstflow)) 

# Peer 2
#################### input  ####################
    srcaddr = srcflow = addr2
    dstaddr = dstflow = addr1

    peer1.host.send_and_return_all( 
    'keyadm add -new -enc aes -auth md5 -spi 603 -dst %s -src %s -ekey \
    b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480 -akey 8317954752bf255b5321fe19e54a7f8d -ingress' \
    % (dstaddr, srcaddr))

    peer1.host.send_and_return_all( \
    'keyadm addflow -spi 603 -dst %s -proto esp -srcmask %s -dstmask %s -srcflow %s -dstflow %s -ingress' \
    % (dstaddr, srcmask, dstmask, srcflow, dstflow))

#################### output  ####################
    srcaddr = srcflow = addr1
    dstaddr = dstflow = addr2

    peer1.host.send_and_return_all( \
    'keyadm add -new -enc aes -auth md5 -spi 603 -dst %s -src %s -ekey \
    b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480 -akey 8317954752bf255b5321fe19e54a7f8d' \
    % (dstaddr, srcaddr))

    peer1.host.send_and_return_all( \
    'keyadm addflow -spi 603 -dst %s -proto esp -srcmask %s -dstmask %s -srcflow %s -dstflow %s' \
    % (dstaddr, srcmask, dstmask, srcflow, dstflow))
#----------------------------------------------------------------------#


def esp_add(self, enc, auth, spi, srcaddr, dstaddr , akey, ekey, ingress):
    lines = self.host.send_and_return_all('keyadm add  -new -enc %s -auth %s -spi %s -dst %s -src %s -ekey %s \
    -akey %s %s' %(enc, auth, spi, dstaddr, srcaddr, ekey, akey, ingress))

def esp_addflow(self, spi, srcaddr, srcmask,  dstaddr , dstmask, akey, ekey, srcflow, dstflow, ingress):
    lines = self.host.send_and_return_all('keyadm addflow -spi %s -dst %s -proto esp -srcmask %s -dstmask %s \
    -srcflow %s -dstflow %s %s' %(spi, dstaddr, srcmask, dstmask, srcflow, dstflow, ingress))

def esp_configure(peer1, peer2, addr1, addr2, v6):
    akey = "8317954752bf255b5321fe19e54a7f8d"
    ekey = "b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480"    
#Configuring ESP with subnet might freeze the target. 

    if v6:
        srcmask = dstmask = "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
    else: 
        srcmask = dstmask = "255.255.255.0"

    enc = "aes"
    auth = "md5"

#Peer 1
    spi = "603"
    srcaddr = srcflow = addr2
    dstaddr = dstflow = addr1
    ingress = '-ingress'

    esp_add(peer1, enc, auth, spi, srcaddr, dstaddr , akey, ekey, ingress)
    esp_addflow(peer1, spi, srcaddr, srcmask,  dstaddr , dstmask, akey, ekey, srcflow, dstflow, ingress)

    spi = "604"
    srcaddr = srcflow = addr1
    dstaddr = dstflow = addr2
    ingress = ""
    esp_add(peer1, enc, auth, spi, srcaddr, dstaddr , akey, ekey, ingress)
    esp_addflow(peer1, spi, srcaddr, srcmask,  dstaddr , dstmask, akey, ekey, srcflow, dstflow, ingress)

#Peer 2
    spi = "603"
    srcaddr = srcflow = addr2
    dstaddr = dstflow = addr1
    ingress = ""
    esp_add(peer2, enc, auth, spi, srcaddr, dstaddr , akey, ekey, ingress)
    esp_addflow(peer2, spi, srcaddr, srcmask,  dstaddr , dstmask, akey, ekey, srcflow, dstflow, ingress)

    spi = '604'
    srcaddr = srcflow = addr1
    dstaddr = dstflow = addr2
    ingress = "-ingress"
    esp_add(peer2, enc, auth, spi, srcaddr, dstaddr , akey, ekey, ingress)
    esp_addflow(peer2, spi, srcaddr, srcmask,  dstaddr , dstmask, akey, ekey, srcflow, dstflow, ingress)

class RohcException(Exception):
    pass

##############################################################
class small_cid:
    'Test ESP profile with small CID'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
	log('Rohc ESP profile test: small_cid', echo=True)
	host1 = hosts[0]
	host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()   
        dut2  = hosts[1].ipcom_shell() 
        
# Configure ROHC on targets   
	peer1 = rohc_base(host1) 
	peer2 = rohc_base(host2) 

        dut1.set_sysvar('iprohc.large_cid', '0')
        dut2.set_sysvar('iprohc.large_cid', '0')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

# Configure ESP
        esp_configure(peer1, peer2, addr1, addr2, v6)

# This code can be reviewed after the activation of the uncompressed  profile to send uncompressed packets.
# The stack might need to negotiate with neighbor nodes when echo-client is invoked.
# These ping operations ensure that ROHC is not configured before such messaging.
#--start--
        if v6:
           peer1.host.send_and_return_all('ping6 -s 1000 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping6 -s 1000 %s' % (addr1_c))
        else:
           peer1.host.send_and_return_all('ping -s 1000 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping -s 1000 %s' % (addr1_c))

#--end--

#Configure ROHC ESP profile 
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '3', '1')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '3', '1')
        peer2.rohc_shell_exit()

# Begin testing  
        dut1.echoserver(addr1_s, proto='udp')
        dut2.echoserver(addr2_s, proto='udp')

# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions     
        dut1.echoclient(addr2_c, proto='udp', nbuf = 10, chunk_size = 1000, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 10, chunk_size = 1000, local_port = 7302, verify_data=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound 
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr2_c, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1_c, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Search for failed decompression
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

#        peer1.rohc_show()
#        peer2.rohc_show()

# Clean up 
        dut1.stop_echoserver()
        dut2.stop_echoserver()           

# Clean up the ROHC  
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()                 
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

# Clean  up ESP 
        peer1.host.send_and_return_all('keyadm flush')
        peer2.host.send_and_return_all('keyadm flush') 


##############################################################
class large_cid:
    'Test ESP profile with large CID and large CID value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc ESP profile test: large_cid', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

# Configure ROHC on targets
        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

        dut1.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '5000')
        dut2.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.max_cid', '5000')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

# Configure ESP
        esp_configure(peer1, peer2, addr1, addr2, v6)

# This code can be reviewed after the activation of the uncompressed  profile to send uncompressed packets.
# The stack might need to negotiate with neighbor nodes when echo-client is invoked.
# These ping operations ensure that ROHC is not configured before such messaging.
#--start--
        if v6:
           peer1.host.send_and_return_all('ping6 -s 1000 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping6 -s 1000 %s' % (addr1_c))
        else:
           peer1.host.send_and_return_all('ping -s 1000 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping -s 1000 %s' % (addr1_c))

#        time.sleep(1)
#--end--

#Configure ROHC ESP profile
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '3', '2000')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '3', '2000')
        peer2.rohc_shell_exit()

# Begin testing
        dut1.echoserver(addr1_s, proto='udp')
        dut2.echoserver(addr2_s, proto='udp')

# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 10, chunk_size = 1000, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 10, chunk_size = 1000, local_port = 7302, verify_data=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr2_c, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1_c, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Search for failed decompression
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

#        peer1.rohc_show()
#        peer2.rohc_show()

# Clean up
        dut1.stop_echoserver()
        dut2.stop_echoserver()

# Clean up the ROHC
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

# Clean  up ESP
        peer1.host.send_and_return_all('keyadm flush')
        peer2.host.send_and_return_all('keyadm flush')

##############################################################
class large_cid_small_val:
    'Test ESP profile with large CID and small value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc ESP profile test: large_cid_small_val', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

# Configure ROHC on targets
        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

        dut1.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '50')
        dut2.set_sysvar('iprohc.max_cid', '50')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

# Configure ESP
        esp_configure(peer1, peer2, addr1, addr2, v6)

# This code can be reviewed after the activation of the uncompressed  profile to send uncompressed packets.
# The stack might need to negotiate with neighbor nodes when echo-client is invoked.
# These ping operations ensure that ROHC is not configured before such messaging.
#--start--
        if v6:
           peer1.host.send_and_return_all('ping6 -s 1000 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping6 -s 1000 %s' % (addr1_c))
        else:
           peer1.host.send_and_return_all('ping -s 1000 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping -s 1000 %s' % (addr1_c))

#        time.sleep(1)
#--end--

#Configure ROHC ESP profile
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '3', '2')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '3', '2')
        peer2.rohc_shell_exit()

# Begin testing
        dut1.echoserver(addr1_s, proto='udp')
        dut2.echoserver(addr2_s, proto='udp')

# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 10, chunk_size = 1000, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 10, chunk_size = 1000, local_port = 7302, verify_data=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr2_c, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1_c, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Search for failed decompression
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

#        peer1.rohc_show()
#        peer2.rohc_show()

# Clean up
        dut1.stop_echoserver()
        dut2.stop_echoserver()

# Clean up the ROHC
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

# Clean  up ESP
        peer1.host.send_and_return_all('keyadm flush')
        peer2.host.send_and_return_all('keyadm flush')

############################################################
class mine_enc_pppoe:
    "ROHC ESP/IP: Mine encapsulation test (GRE)"
    def config(self):
        self.hosts = 3
        self.eta = 6
        self.v6 = False
        self.works_on_iplite = False
        self.works_on_gpp = False

    def test(self, log,  hosts, v6, _):
        nut1, nut2, nut3 = hosts

# Configure PPPoE and ROHC
        dut1  = nut1.ipcom_shell()
        dut2  = nut2.ipcom_shell()

# Configure ROHC on targets
        peer1 = rohc_base(nut1)
        peer2 = rohc_base(nut2)

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

#Configure tunnel 
        addr1, addr2, tunnel_ifs  = test_setup(log, "min", nut1, nut2, addr1_c, addr2_c, 17, v6)

# Configure ESP
        esp_configure(peer1, peer2, addr1, addr2, v6)

#Configure ROHC ESP profile
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '3', '2')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '3', '2')
        peer2.rohc_shell_exit()

# Begin testing
        dut1.echoserver(addr1, proto='udp')
        dut2.echoserver(addr2, proto='udp')

# Test a connection for short packets
        dut1.echoclient(addr2, proto='udp', nbuf = 1, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='udp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection for long packets 
        dut1.echoclient(addr2, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#       dut1.echoclient(addr2, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)
#       dut2.echoclient(addr1, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)

# Test 2 connections with the same destination port
        dut1.echoclient(addr2, proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.echoclient(addr2, proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True, reuse_addr=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(addr1, proto='udp', port = 7307)
        dut2.echoserver(addr2 ,proto='udp', port = 7307)
        dut1.echoclient(addr2, proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='udp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True, reuse_addr=True)

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)

        dut1.stop_echoserver()
        dut2.stop_echoserver()

        for t in tunnel_ifs:
           t.destroy()

        return

############################################################
def send_pkts(csock, ssock, addr_dst, port_dst, num_pkts, anc_data):
     data = "*012345678901234567890123456789012345678901234567890123456789!"
     data_len = len(data)
     i = 1
     while i <=  num_pkts:
        i += 1
        csock.send(data, addr=addr_dst, port=port_dst, ancillary_data=anc_data)
        ssock.recv(exp_len = data_len)

############################################################
class hop_dst_opt_pppoe:
    'Test ROHC ESP/IP: Test hop by hop, dst options'
    def config(self):
        self.hosts = 3
        self.v6 = True
        self.v4 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()

# Configure ROHC on targets
        peer1 = rohc_base(hosts[0])
        peer2 = rohc_base(hosts[1])

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)
        addr = addr2_c
# Configure ESP
        esp_configure(peer1, peer2, addr1, addr2, v6)

#Configure ROHC ESP profile
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '3', '2')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '3', '2')
        peer2.rohc_shell_exit()

# Begin testing
        def internal(c,s):
            _sport = s.alloc_port()

            ssock = s.socket('inet'+v6, 'datagram', 'udp')
            ssock.setsockopt('ipv6', 'dstopt', 1)
            ssock.setsockopt('ipv6', 'hopopt', 1)
            ssock.bind(port = _sport)

            csock = c.socket('inet'+v6, 'datagram', 'udp')
            
            peer1.host.send_and_return_all('ping6 -s 1000 %s' % (addr2_c))
            peer2.host.send_and_return_all('ping6 -s 1000 %s' % (addr1_c))

            pkt_num = 10

            send_pkts(csock, ssock, addr, _sport, pkt_num, '')

            p = 'ipv6'
            opt_v = 'nop'

            o = 'dstopt'
            csock.setsockopt(p, o, opt_v)
            ssock.setsockopt(p, o, 1)
            send_pkts(csock, ssock,  addr, _sport, pkt_num, '')

            o = 'hopopt'
            csock.setsockopt(p, o, opt_v)
            ssock.setsockopt(p, o, 1)
            send_pkts(csock, ssock,  addr, _sport, pkt_num, '')

            ssock.close()
            csock.close()
        internal(c,s)
#Swap  PPPoE addresses
#        addr = addr1_c
#        internal(s,c)
# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)
