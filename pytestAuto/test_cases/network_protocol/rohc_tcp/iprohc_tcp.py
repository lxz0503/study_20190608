#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


#import re
#import util
#import subprocess
#import pexpect
#import socket
#import time
#import threading
#import time
#import pdb
#import string

from util import IF
from iprohc_common import *
from tunnel import _test_setup, _test_tunnel, _has_ipv6_support 

############################################################
def  config_pppoe_rohc(hosts, v6):
    host1 = hosts[0]
    host2 = hosts[1]
    peer1 = rohc_base(host1)
    peer2 = rohc_base(host2)
    s, c = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()

# small CID
    s.set_sysvar('iprohc.large_cid', '1')
    c.set_sysvar('iprohc.large_cid', '1')
    s.set_sysvar('iprohc.max_cid', '50')
    c.set_sysvar('iprohc.max_cid', '50')

# Configure PPPoE
    addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6 = v6)

# Prepare PPPoE addresses for use
    addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

# This code can be reviewed after activation of the uncompressed  profile to send uncompressed packets.
# The stack might need to negotiate with neighbor nodes when echo-client is invoked.
# These ping operations ensure that ROHC is not configured before such messaging.
#--start--
    if v6:
        peer1.host.send_and_return_all('ping6 -s 1000 %s' % (addr2_c))
        peer2.host.send_and_return_all('ping6 -s 1000 %s' % (addr1_c))
    else:
        peer1.host.send_and_return_all('ping -s 1000 %s' % (addr2_c))
        peer2.host.send_and_return_all('ping -s 1000 %s' % (addr1_c))

    time.sleep(1)
#--end--

# Configure ROHC
    peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '6', '1')
    peer1.rohc_shell_exit()
    peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '6', '1')
    peer2.rohc_shell_exit()

    return (addr1_c, addr2_c, addr1_s, addr2_s)


############################################################
def  validate_and_cleanup_rohc(hosts):
    host1 = hosts[0]
    host2 = hosts[1]
    peer1 = rohc_base(host1)
    peer2 = rohc_base(host2)

    peer1.lookup_for_failed_decompression()
    peer2.lookup_for_failed_decompression()

# Clean up the ROHC
    peer1.rohc_shell_start()
    peer1.rohc_close()
    peer1.rohc_shell_exit()
    peer2.rohc_shell_start()
    peer2.rohc_close()
    peer2.rohc_shell_exit()


############################################################
class accept_pppoe:
    'ROHC TCP/IP profile: Tests failed accept() cases.'
    def config(self):
        self.eta = 4
        self.hosts = 3
        self.works_on_iplite = True

    def test(self, log, hosts, v6, _):
        s, c = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()
        sport = s.alloc_port()

# Configure PPPoE and ROHC
        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)

        log("Create server listen socket")
        ssock = s.socket('inet' + v6, 'stream', 'tcp')
        ssock.bind(port = sport)
        log('Check that the SO_ACCEPTCONN works')
        if int(ssock.getsockopt('socket', 'acceptconn')) != 0:
            raise "getsockopt acceptconn must return 0 before listen()"
        ssock.listen()
        if int(ssock.getsockopt('socket', 'acceptconn')) != 1:
            raise "getsockopt acceptconn must return 1 after listen()"

        log("Create client socket with a linger time of zero -> RST will be sent on close")
        csock = c.socket('inet' + v6, 'stream', 'tcp')
        csock.setsockopt('socket', 'linger', 0)

# Use PPPoE connection
        csock.connect(addr1_c, sport)

        if int(csock.getsockopt('socket', 'acceptconn')) != 0:
            raise "getsockopt acceptconn must return 0 since listen() has not been called"
        csock.close()

        log("Accept should now return 'Software caused connection abort'")
        ssock.accept_pre()
#        s.expect("Failed, errno: Software caused connection abort")
        s.wait_prompt()
        ssock.close()

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)


############################################################
class sockopt_pppoe:
    'Test ROHC TCP/IP profile with TCP socket option "linger".'
    def config(self):
        self.hosts = 3
        self.v6 = False
        self.works_on_iplite = True

    def test(self, log, hosts, v6, _):
        c, s = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()

# Configure PPPoE and ROHC
        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr = addr2_c

        def internal(c,s):
            for is_on in False, True:
                _sport = s.alloc_port()
                if is_on:
                    log("Test closedown when linger is set to 1 second")
                else:
                    log("Test closedown when linger is off")

                ssock = s.socket('inet'+v6, 'stream', 'tcp')
                ssock.bind(port = _sport)
                ssock.listen()

                csock = c.socket('inet'+v6, 'stream', 'tcp')
                csock.getsockopt('socket', 'linger', exp_data = 'off')
                if is_on:
                    csock.setsockopt('socket', 'linger', 0)

# Use PPPoE connection
                csock.connect(addr, _sport)
                asock = ssock.accept()
                ssock.close()
                csock.close()
                asock.close()
        internal(c,s)
# Swap  PPPoE addresses
        addr = addr1_c
        internal(s,c)
# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)


############################################################
class ttl_hlim_pppoe:
    'Test ROHC TCP/IP profile with static/irregular ttl_hlim/dscp/ecn values for inner ip header'
    def config(self):
        self.hosts = 3
        self.v6 = True 
        self.v4 = True 
        self.works_on_iplite = True

    def test(self, log, hosts, v6, _):
        c, s = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()
     
# Configure PPPoE and ROHC
        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr = addr2_c

        def internal(c,s):
            for is_on in False, True:
                _sport = s.alloc_port()
                if is_on:
                    log("Test closedown when linger is set to 1 second")
                else:
                    log("Test closedown when linger is off")

                ssock = s.socket('inet'+v6, 'stream', 'tcp')
                ssock.bind(port = _sport)
                ssock.listen()

                csock = c.socket('inet'+v6, 'stream', 'tcp')
                csock.getsockopt('socket', 'linger', exp_data = 'off')
                if is_on:
                    csock.setsockopt('socket', 'linger', 0)

                pkt_num = 1

# Use PPPoE connection
                csock.connect(addr, _sport)
                asock = ssock.accept()
                send_pkts(csock, asock, pkt_num)

# Exercise inner ip header ecn flags   
# p - socket level, t - tos/tclass 
                if not v6:
                    p = 'ip' 
                    t = 'tos'
                    t_h = 'ttl'
                else: 
                    p = 'ipv6'
                    t = 'tclass'
                    t_h = 'unicast_hops'

                ecn_p = ('2', '0', '1', '0', '3', '0', '3', '1', '2', '3', '2', '1', '0', '0', '0', '13', '14', '15') 
                num = len(ecn_p)
               
                for i in range(0, num):   
#                    print "-----------------------------------"
#                    print p, t
#                    print "prev option", csock.getsockopt(p, t)
#                    print "new option", ecn_p[i]
                    csock.setsockopt(p, t, ecn_p[i])
#                    print "new option set", csock.getsockopt(p, t)
                    send_pkts(csock, asock, pkt_num)
                    
                dscp_p = ('4', '128', '240', '4', '4', '4', '3', '3', '1', '0' , '0', '4','4', '13', '14', '15')
                num = len(dscp_p)
                for i in range(0, num):
#                    print "-------------------------------------"
#                    print p, t
#                    print "prev dscp", csock.getsockopt(p, t) 
#                    print "new option", dscp_p[i]
                    csock.setsockopt(p, t, dscp_p[i])
#                    print "new option set",  csock.getsockopt(p, t)
                    send_pkts(csock, asock, pkt_num)

                t_h_p = ('0','0', '1', '1', '0', '1', '1', '0', '0', '100', '100')
                num = len(t_h_p)
                for i in range(0, num):
#                    print "---------------------------------------"
#                    print p, t_h
#                    print "prev option", csock.getsockopt(p, t_h)
#                    print "new option", t_h_p[i] 
                    csock.setsockopt(p, t_h, t_h_p[i])
#                    print "new option set",  csock.getsockopt(p, t_h)
                    send_pkts(csock, asock, pkt_num)

                ssock.close()
                csock.close()
                asock.close()
        internal(c,s)
# Swap  PPPoE addresses
        addr = addr1_c
        internal(s,c)
# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)


def send_pkts(csock, asock, num_pkts):  
     data = "*012345678901234567890123456789012345678901234567890123456789012345678900123456789001234567890!"
     data_len = len(data)
     i = 1
     while i <=  num_pkts:
        i += 1
        csock.send(data)
        asock.recv(exp_len = data_len)


############################################################
class ipip_ttl_hlim_pppoe:
    'Test ROHC TCP/IP profile with static/irregular ttl_hlim/dscp/ecn values for ipip headers'
    def config(self):
        self.hosts = 3
        self.eta = 6
        self.v6 = False
        self.works_on_iplite = False
        self.works_on_gpp = False
        self.v4 = True

    def test(self, log,  hosts, v6, _):
        c, s = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()
 
# Configure PPPoE and ROHC
        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr1, addr2, tunnel_ifs  = test_setup(log, "ip", hosts[0], hosts[1], addr1_c, addr2_c, 17, v6)

        addr = addr2

        def internal(c,s):
            for is_on in False, True:
                _sport = s.alloc_port()
                if is_on:
                    log("Test closedown when linger is set to 1 second")
                else:
                    log("Test closedown when linger is off")

                ssock = s.socket('inet'+v6, 'stream', 'tcp')
                ssock.bind(port = _sport)
                ssock.listen()

                csock = c.socket('inet'+v6, 'stream', 'tcp')
                csock.getsockopt('socket', 'linger', exp_data = 'off')
                if is_on:
                    csock.setsockopt('socket', 'linger', 0)

                pkt_num = 1

# Use PPPoE connection
                csock.connect(addr, _sport)
                asock = ssock.accept()
                send_pkts(csock, asock, pkt_num)

# p - socket level, t - tos/tclass
                if not v6:
                    p = 'ip'
                    t = 'tos'
                    t_h = 'ttl'
                else:
                    p = 'ipv6'
                    t = 'tclass'
                    t_h = 'unicast_hops'

# Test inner and outer header's ecn
                ecn_p = ('2', '0', '1', '0', '3', '0', '3', '1', '2', '3', '2', '1', '0', '0', '0', '13', '14', '15')
                num = len(ecn_p)
                for i in range(0, num):
#                    print "-----------------------------------"
#                    print p, t
#                    print "prev option", csock.getsockopt(p, t)
#                    print "new option", ecn_p[i]
                    csock.setsockopt(p, t, ecn_p[i])
#                    print "new option set", csock.getsockopt(p, t)
                    send_pkts(csock, asock, pkt_num)

# Test inner and outer header's dscp 
                dscp_p = ('3', '3', '1', '0' , '0', '13', '14', '15', '17', '17', '17', '0' , '0' )
                num = len(dscp_p)
                for i in range(0, num):
#                    print "-------------------------------------"
#                    print p, t
#                    print "prev dscp", csock.getsockopt(p, t)
#                    print "new option", dscp_p[i]
                    csock.setsockopt(p, t, dscp_p[i])
#                    print "new option set",  csock.getsockopt(p, t)
                    send_pkts(csock, asock, pkt_num)

# Test inner headr's ttl_hlim
                t_h_p = ('0','0', '1', '1', '0', '1', '1', '0', '0', '100', '100')
                num = len(t_h_p)
                for i in range(0, num):
#                    print "---------------------------------------"
#                    print p, t_h
#                    print "prev option", csock.getsockopt(p, t_h)
#                    print "new option", t_h_p[i]
                    csock.setsockopt(p, t_h, t_h_p[i])
#                    print "new option set",  csock.getsockopt(p, t_h)
                    send_pkts(csock, asock, pkt_num)

# Test outer headr's ttl_hlim
                u_t_h_p = ('0','0', '1', '1', '0', '1', '1', '0', '0', '100', '100')                
                num = len(u_t_h_p) 
                for i in range(0, num):
                     hosts[0].send_and_return_all('ifconfig %s inet tunnel %s %s %s' % \
                                          (tunnel_ifs[0].ifname, addr1_c, addr2_c,  u_t_h_p[i]))
                     hosts[1].send_and_return_all('ifconfig %s inet tunnel  %s %s %s' % \
                                          (tunnel_ifs[1].ifname, addr2_c, addr1_c,  u_t_h_p[i]))
                     send_pkts(csock, asock, pkt_num)

                ssock.close()
                csock.close()
                asock.close()
        internal(c,s)
# Swap  PPPoE addresses
        addr = addr1_c
        internal(s,c)
# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)

        for t in tunnel_ifs:
           t.destroy()

        return


############################################################
class ipip_pppoe:
    "ROHC TCP/IP: Connectivity and tos propagation for IPIP/GIF tunnels"
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

        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr1, addr2, tunnel_ifs  = test_setup(log, "ip", nut1, nut2, addr1_c, addr2_c, 17, v6)

# Begin testing
        dut1.echoserver(addr1, proto='tcp')
        dut2.echoserver(addr2, proto='tcp')

# Test a connection for short packets
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='tcp', nbuf = 1, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#       dut1.echoclient(addr2, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)
#       dut2.echoclient(addr1, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)


# Test 2 connections with the same destination port
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(addr1, proto='tcp', port = 7307)
        dut2.echoserver(addr2 ,proto='tcp', port = 7307)
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)

        dut1.stop_echoserver()
        dut2.stop_echoserver()

        for t in tunnel_ifs:
           t.destroy()

        return

def has_ipv6_support(nut):
    lines = nut.send_and_return_all('ping6')
    for line in lines:
        if 'Unknown command' in line or 'command not found' in line:
            return False
    return True

def _test_tunnel(log, nut1, nut2, tunnel_addrs, v6):
    log('Verify connectivity through the tunnel')

    nut1.ping(tunnel_addrs[1], count = 1, retries = 4)
    nut2.ping(tunnel_addrs[0], count = 1, retries = 4)

    snut1 = nut1.ipcom_shell()
    snut2 = nut2.ipcom_shell()

    s1, s2 = snut1.create_connected_socket_pair(snut2, v6 = v6, server_addr = tunnel_addrs[1])

    log('Send some data trough the tunnel')
    for y in range(1, 5):
        data = ('%d' % y) * y
        s1.send(data)
        s2.recv(exp_data = data)

    for y in range(5, 10):
        data = ('%d' % y) * y
        s2.send(data)
        s1.recv(exp_data = data)

    s1.close()
    s2.close()


def test_setup(log, type, nut1, nut2, addr1, addr2, tunnel_net, v6='', treat_as_ppp = True):

    tunnel_addrs = (nut1.alloc_ip(v6 = v6, net = tunnel_net),
                    nut2.alloc_ip(v6 = v6, net = tunnel_net))

    tunnel_ifs = (nut1.add_netif(addr = tunnel_addrs[0],
                                 tunnel = type,
                                 tunnel_local_ip = addr1,
                                 tunnel_remote_ip = addr2),
                  nut2.add_netif(addr = tunnel_addrs[1],
                                 tunnel = type,
                                 tunnel_local_ip = addr2,
                                 tunnel_remote_ip = addr1))

    if treat_as_ppp:
        nut1.send_and_return_all('ifconfig %s inet dstaddr %s'
                                 % (tunnel_ifs[0].ifname, tunnel_addrs[1].addr))
        nut2.send_and_return_all('ifconfig %s inet dstaddr %s'
                                 % (tunnel_ifs[1].ifname, tunnel_addrs[0].addr))

# Test connectivity
#    _test_tunnel(log, nut1, nut2, tunnel_addrs, v6 = v6)

#    for t in tunnel_ifs:
#        t.destroy()
    return (tunnel_addrs[0], tunnel_addrs[1], tunnel_ifs)


############################################################
#Test tunneling.  Currently this test case runs on  Ethernet ports only
#which introduces some limitations.  The compressed packets should not
#be shorter than the Ethernet frame length. In order to use this test
#case - adjust the length of the packet filter to avoid the compression
#of the short packets.  Some packets will bypass the compression.
#This is just a workaround for testing. Also, make sure that there
#are no TCP packets (like telnet session etc. ) which should not be
#compressed on interfaces on which the tcp profile is configured.
#This test cases needs to be modified to run over  PPPoE interfaces.

class ipip:
    "ROHC TCP/IP profile: Connectivity and tos propagation for IPIP/GIF tunnels"
    def config(self):
        self.hosts = 2
        self.eta = 6
        self.v4 = False

# Run this test case manually only.
        self.v6 = False 

        self.works_on_iplite = False
        self.works_on_gpp = False

    def test(self, log, hosts, v6, _):
        nut1, nut2 = hosts
        addr1, addr2, tunnel_ifs  = test_setup(log, "ip", nut1, nut2, nut1.ip(), nut2.ip(), 17, v6, treat_as_ppp = False)

# Configure PPPoE and ROHC
        dut1  = nut1.ipcom_shell()
        dut2  = nut2.ipcom_shell()

# Small CID
        dut1.set_sysvar('iprohc.large_cid', '0')
        dut2.set_sysvar('iprohc.large_cid', '0')

# Configure ROHC on targets peer1 and peer2
        host1 = hosts[0]
        host2 = hosts[1]

        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

        peer1.rohc_configure('eth', '0', 'eth0', '6', '1')
        peer1.rohc_shell_exit()
        peer2.rohc_configure('eth', '0', 'eth0', '6', '1')
        peer2.rohc_shell_exit()

# Begin testing
        dut1.echoserver(addr1, proto='tcp')
        dut2.echoserver(addr2, proto='tcp')

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)

        dut1.stop_echoserver()
        dut2.stop_echoserver()

        for t in tunnel_ifs:
           t.destroy()

        return


############################################################
class small_cid:
    'Test TCP profile with small CID'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
	log('Rohc TCP profile test: small_cid', echo=True)
	host1 = hosts[0]
	host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()   
        dut2  = hosts[1].ipcom_shell() 
        
	peer1 = rohc_base(host1) 
	peer2 = rohc_base(host2) 

# Small CID
        dut1.set_sysvar('iprohc.large_cid', '0')
        dut2.set_sysvar('iprohc.large_cid', '0')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6 = v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

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

# Configure ROHC
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '6', '1')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '6', '1')
        peer2.rohc_shell_exit()

# Use 'sleep' for debugging only
#        if v6:
#        time.sleep(5000) 

# Begin testing  
# Between ports 7302/7301 in both directions
        dut1.echoserver(addr1_s, proto='tcp')
        dut2.echoserver(addr2_s, proto='tcp')

# Test a connection for short packets
# Between ports 7302/7301 in both directions     
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound 
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr2_c, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)
#        dut2.echoclient(addr1_c, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)

# Test 2 connections with the same destination port
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(addr1_s, proto='tcp', port = 7307)
        dut2.echoserver(addr2_s ,proto='tcp', port = 7307)
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)


# Search for failed decompression
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

# Clean up the ROHC  
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()                 
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

# Clean up 
        dut1.stop_echoserver()
        dut2.stop_echoserver()           

############################################################
class large_cid:
    'Test TCP profile with large CID and large CID value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc TCP profile test: large_cid', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

# Large CID
        dut1.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '5000')
        dut2.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.max_cid', '5000')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6 = v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

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

        time.sleep(1)
#--end--

# Configure ROHC
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '6', '1')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '6', '1')
        peer2.rohc_shell_exit()

# Use 'sleep' for debugging only
#        if v6:
#           time.sleep(5000)

# Begin testing
# Between ports 7302/7301 in both directions
        dut1.echoserver(addr1_s, proto='tcp')
        dut2.echoserver(addr2_s, proto='tcp')

# Test a connection for short packets
# Between ports 7302/7301 in both directions

        dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#       dut1.echoclient(addr2_c, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)
#       dut2.echoclient(addr1_c, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)

# Test 2 connections with the same destination port
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(addr1_s, proto='tcp', port = 7307)
        dut2.echoserver(addr2_s ,proto='tcp', port = 7307)
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)

# Search for failed decompression
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

# Clean up the ROHC
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

# Clean up
        dut1.stop_echoserver()
        dut2.stop_echoserver()

############################################################
class large_cid_small_val:
    'Test TCP profile with large CID and small value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc TCP profile test: large_cid_small_val', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

        dut1.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '50')
        dut2.set_sysvar('iprohc.max_cid', '50')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6 = v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

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

        time.sleep(1)
#--end--

# Configure ROHC
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '6', '1')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '6', '1')
        peer2.rohc_shell_exit()

# Use 'sleep' for debugging only
#        time.sleep(5000)

# Begin testing
# Between ports 7302/7301 in both directions
        dut1.echoserver(addr1_s, proto='tcp')
        dut2.echoserver(addr2_s, proto='tcp')

# Test a connection for short packets
# Between ports 7302/7301 in both directions

        dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#       dut1.echoclient(addr2_c, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)
#       dut2.echoclient(addr1_c, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)

# Test 2 connections with the same destination port
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(addr1_s, proto='tcp', port = 7307)
        dut2.echoserver(addr2_s ,proto='tcp', port = 7307)
        dut1.echoclient(addr2_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1_c, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)

# Search for failed decompression
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

# Clean up the ROHC
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

# Clean up
        dut1.stop_echoserver()
        dut2.stop_echoserver()


########## Run ipnet2 tcp test cases ########## 
class ip6_ip4_pppoe:
    "ROHC TCP/IP profile: Transmission of IPv6 over IPv4 Domains without Explicit Tunnels (RFC 2529)"
    def config(self):
        self.hosts = 3
        self.v6 = False  
        self.eta = 6
        self.works_on_iplite = False
        self.works_on_gpp = False

    def test(self, log, hosts, v6, _):
        nut1, nut2, nut3 = hosts

        log('6over4 tunnel: both targets must have IPv4 and IPv6 support')
        if _has_ipv6_support(nut1) == False or _has_ipv6_support(nut2) == False:
            return 'skipped'

# Configure PPPoE and ROHC
        dut1  = nut1.ipcom_shell()
        dut2  = nut2.ipcom_shell()

        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)

        tunnel_addrs = (nut1.alloc_ip(v6 = '6'),
                        nut2.alloc_ip(v6 = '6'))

        tunnel_ifs = (nut1.add_netif(addr = tunnel_addrs[0],
                                     tunnel = "ip",
                                     tunnel_local_ip = addr1_c,
                                     tunnel_remote_ip = addr2_c),
                      nut2.add_netif(addr = tunnel_addrs[1],
                                     tunnel = "ip",
                                     tunnel_local_ip = addr2_c,
                                     tunnel_remote_ip = addr1_c))

        nut1.send_and_return_all('ifconfig %s inet dstaddr %s'
                                 % (tunnel_ifs[0].ifname, tunnel_addrs[1].addr))
        nut2.send_and_return_all('ifconfig %s inet dstaddr %s'
                             % (tunnel_ifs[1].ifname, tunnel_addrs[0].addr))

        addr1 = tunnel_addrs[0]
        addr2 = tunnel_addrs[1] 

        dut1.echoserver(addr1, proto='tcp')
        dut2.echoserver(addr2, proto='tcp')

        dut1.echoclient(addr2, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)
        dut1.stop_echoserver()
        dut2.stop_echoserver()

        for t in tunnel_ifs:
            t.destroy()


############################################################
class tcp_opt_common:
    'Test ROHC TCP/IP profile tcp common options'
    def config(self):
        self.hosts = 3
        self.v6 = True
        self.v4 = True

    def test(self, log, hosts, v6, _):
        c, s = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()

# Configure PPPoE and ROHC
        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr = addr2_c

        def internal(c,s):
            for is_on in False, True:
                _sport = s.alloc_port()
                if is_on:
                    log("Test closedown when linger is set to 1 second")
                else:
                    log("Test closedown when linger is off")

                ssock = s.socket('inet'+v6, 'stream', 'tcp')
                ssock.bind(port = _sport)
                ssock.listen()

                csock = c.socket('inet'+v6, 'stream', 'tcp')
                csock.getsockopt('socket', 'linger', exp_data = 'off')
                if is_on:
                    csock.setsockopt('socket', 'linger', 0)

                pkt_num = 3
                p = 'tcp'

                csock.connect(addr, _sport)
                asock = ssock.accept()
                send_pkts(csock, asock, pkt_num)

                # maxseg
#                print "-----------------------------------"
                o = 'maxseg'
                v = '300'
#                print p, o
#                print "prev option", csock.getsockopt(p, o)
#                print "new option", v
                csock.setsockopt(p, o, v)
#                print "new option set", csock.getsockopt(p, o)
                send_pkts(csock, asock, pkt_num)

                # timestamp
                o = 'iptcp.opt.Timestamp'
                tsop  = ('1', '0', '1', '0')
                num = len(tsop)
                for i in range(0, num):
#                    print "-----------------------------------"
#                    print "prev option",  c.get_sysvar(o)
#                    print "new option", tsop[i]
                    c.set_sysvar(o, tsop[i])
#                    print "new option set", c.get_sysvar(o)
                    send_pkts(csock, asock, pkt_num)

                ssock.close()
                csock.close()
                asock.close()
        internal(c,s)
# Swap  PPPoE addresses
        addr = addr1_c
        internal(s,c)
# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)


############################################################
class tcp_opt_generic:
    'Test ROHC TCP/IP profile TCP generic options'
    def config(self):
        self.hosts = 3
        self.v6 = True
        self.v4 = True

    def test(self, log, hosts, v6, _):
        c, s = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()

# Configure PPPoE and ROHC
        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr = addr2_c

        def internal(c,s):
            for is_on in False, True:
                _sport = s.alloc_port()
                if is_on:
                    log("Test closedown when linger is set to 1 second")
                else:
                    log("Test closedown when linger is off")

                ssock = s.socket('inet'+v6, 'stream', 'tcp')
                ssock.bind(port = _sport)
                ssock.listen()

                csock = c.socket('inet'+v6, 'stream', 'tcp')
                csock.getsockopt('socket', 'linger', exp_data = 'off')
                if is_on:
                    csock.setsockopt('socket', 'linger', 0)

                pkt_num = 3

                # TCP MD5 option (set before connect, accept)
#                print "-----------------------------------"
                p = 'tcp'
                t = 'md5key'
                o = 'md5authenticationkey'

#                print p, t
#                print "client: prev option", csock.getsockopt(p, t)
#                print "new option", o
                csock.setsockopt(p, t, o)
#                print "new option set", csock.getsockopt(p, t)

#                print "server: prev option", ssock.getsockopt(p, t)
#                print "new option", o
                ssock.setsockopt(p, t, o)
#                print "new option set", ssock.getsockopt(p, t)
                                                                                             
                csock.connect(addr, _sport)
                asock = ssock.accept()

                # Test TCP MD5 option
                send_pkts(csock, asock, pkt_num)

#                print "-----------------------------------"
                o = 'maxseg'
                v = '300'
#                print p, o
#                print "prev option", csock.getsockopt(p, o)
#                print "new option", v
                csock.setsockopt(p, o, v)
#                print "new option set", csock.getsockopt(p, o)
                send_pkts(csock, asock, pkt_num)

                o = 'iptcp.opt.Timestamp'
                tsop  = ('1', '0', '1', '0')
                num = len(tsop)
                for i in range(0, num):
#                    print "-----------------------------------"
#                    print "prev option",  c.get_sysvar(o)
#                    print "new option", tsop[i]
                    c.set_sysvar(o, tsop[i])
#                    print "new option set", c.get_sysvar(o)
                    send_pkts(csock, asock, pkt_num)

                ssock.close()
                csock.close()
                asock.close()
        internal(c,s)
# Swap  PPPoE addresses
        addr = addr1_c

        internal(s,c)
# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)


############################################################
class mine_enc_pppoe:
    "ROHC IP: Mine encapsulation test (GRE)"
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

        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr1, addr2, tunnel_ifs  = test_setup(log, "min", nut1, nut2, addr1_c, addr2_c, 17, v6)

# Begin testing
        dut1.echoserver(addr1, proto='tcp')
        dut2.echoserver(addr2, proto='tcp')

# Test a connection for short packets
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='tcp', nbuf = 1, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)


# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#       dut1.echoclient(addr2, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)
#       dut2.echoclient(addr1, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)


# Test 2 connections with the same destination port
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7305, verify_data=True, reuse_addr=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7306, verify_data=True, reuse_addr=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(addr1, proto='tcp', port = 7307)
        dut2.echoserver(addr2 ,proto='tcp', port = 7307)
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 100, local_port = 7301, port = 7307, verify_data=True, reuse_addr=True)

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)

        dut1.stop_echoserver()
        dut2.stop_echoserver()

        for t in tunnel_ifs:
           t.destroy()

        return

##########################################################
# Test IP ID compression for variouse change patterns.  
# Incremental, random, 0 IP IDs are supported
############################################################

############################################################
class ipid_pppoe:
    'ROHC TCP/IP: Test ip id compression for ip in ip tunnels'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc TCP profile test: small_cid', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

# Small CID
        dut1.set_sysvar('iprohc.large_cid', '0')
        dut2.set_sysvar('iprohc.large_cid', '0')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6 = v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

        if v6:
            peer1.host.send_and_return_all('ping6 -s 1000 %s' % (addr2_c))
            peer2.host.send_and_return_all('ping6 -s 1000 %s' % (addr1_c))
        else:
            peer1.host.send_and_return_all('ping -s 1000 %s' % (addr2_c))
            peer2.host.send_and_return_all('ping -s 1000 %s' % (addr1_c))

#        time.sleep(1)

        def internal(ipid_sim):
     
# Configure ROHC
            peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '6', '1')
            peer1.rohc_shell_exit()
            peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '6', '1')
            peer2.rohc_shell_exit()

# Set IP_ID change pattern. For IPv4 Incremental, RND, 0
            peer1.rohc_shell_start()
            lines = peer1.host.send_and_return_all('ifadd -ifname %s -ifnum %s' %('xrohc', ipid_sim))
            peer1.rohc_shell_exit()
            peer2.rohc_shell_start()
            lines = peer2.host.send_and_return_all('ifadd -ifname %s -ifnum %s' %('xrohc', ipid_sim))
            peer2.rohc_shell_exit()


# Begin testing
# Between ports 7302/7301 in both directions
            if v6:
                dut1.echoserver(addr1_s, proto='tcp')
                dut2.echoserver(addr2_s, proto='tcp')
            else:
                dut1.echoserver(addr1_c, proto='tcp')
                dut2.echoserver(addr2_c, proto='tcp')

            dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302+ipid_sim, verify_data=True, reuse_addr=True)
            dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302+ipid_sim, verify_data=True, reuse_addr=True)


# Search for failed decompression
            peer1.lookup_for_failed_decompression()
            peer2.lookup_for_failed_decompression()

# Clean up the ROHC
            peer1.rohc_shell_start()
            peer1.rohc_close()
            peer1.rohc_shell_exit()
            peer2.rohc_shell_start()
            peer2.rohc_close()
            peer2.rohc_shell_exit()
# Clean up
            dut1.stop_echoserver()
            dut2.stop_echoserver()

        internal(0)
        internal(1)
        if not v6:
           internal(2)
           internal(3)


############################################################
class ipid_ip_ip_pppoe:
    "ROHC TCP/IP: Test ip id compression for ip in ip tunnels"
    def config(self):
        self.hosts = 3
        self.eta = 6
        self.v6 = False
        self.works_on_iplite = False
        self.works_on_gpp = False

    def test(self, log,  hosts, v6, _):
        nut1, nut2, nut3 = hosts

        peer1 = rohc_base(hosts[0])
        peer2 = rohc_base(hosts[1])

# Configure PPPoE and ROHC
        dut1  = nut1.ipcom_shell()
        dut2  = nut2.ipcom_shell()

        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr1, addr2, tunnel_ifs  = test_setup(log, "ip", nut1, nut2, addr1_c, addr2_c, 17, v6)

        def internal(ipid_sim):

# Set IP_ID change pattern. For IPv4 Incremental, RND, 0
            peer1.rohc_shell_start()
            lines = peer1.host.send_and_return_all('ifadd -ifname %s -ifnum %s' %('xrohc', ipid_sim))
            peer1.rohc_shell_exit()
            peer2.rohc_shell_start()
            lines = peer2.host.send_and_return_all('ifadd -ifname %s -ifnum %s' %('xrohc', ipid_sim))
            peer2.rohc_shell_exit()

# Begin testing
            dut1.echoserver(addr1, proto='tcp')
            dut2.echoserver(addr2, proto='tcp')

# Between ports 7302/7301 in both directions
            dut1.echoclient(addr2, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302+ipid_sim, verify_data=True, reuse_addr=True)
            dut2.echoclient(addr1, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302+ipid_sim, verify_data=True, reuse_addr=True)

# Validate and celan up ROHC
#            validate_and_cleanup_rohc(hosts)

            dut1.stop_echoserver()
            dut2.stop_echoserver()

# Search for failed decompression
            peer1.lookup_for_failed_decompression()
            peer2.lookup_for_failed_decompression()

        internal(0)
        internal(1)
        internal(2)
        internal(3)

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)

        for t in tunnel_ifs:
           t.destroy()

        return


##########################################################
# Test more than one configured profile   
############################################################

############################################################
class n_profles:
    'Test more than one configured profile'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc multiple profiles test', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

# Small CID
        dut1.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.large_cid', '1')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6 = v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

        if v6:
            peer1.host.send_and_return_all('ping6 -s 1000 %s' % (addr2_c))
            peer2.host.send_and_return_all('ping6 -s 1000 %s' % (addr1_c))
        else:
            peer1.host.send_and_return_all('ping -s 1000 %s' % (addr2_c))
            peer2.host.send_and_return_all('ping -s 1000 %s' % (addr1_c))

        def internal():

# Configure ROHC TCP profile
           peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, "6", '2')
           peer1.rohc_shell_exit()
           peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, "6", '2')
           peer2.rohc_shell_exit()

           if v6:
               dut1.echoserver(addr1_s, proto='tcp')
               dut2.echoserver(addr2_s, proto='tcp')
           else:               
               dut1.echoserver(addr1_c, proto='tcp')
               dut2.echoserver(addr2_c, proto='tcp')

           dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
           dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
           peer1.lookup_for_failed_decompression()
           peer2.lookup_for_failed_decompression()
           dut1.stop_echoserver()
           dut2.stop_echoserver()

# Configure ROHC UDP profile
           peer1.rohc_add_profile(if_name1[:5], if_name1[5:], if_name1, '2', '2')
           peer1.rohc_shell_exit()
           peer2.rohc_add_profile(if_name2[:5], if_name2[5:], if_name2, '2', '2')
           peer2.rohc_shell_exit()

           dut1.echoserver(addr1_s, proto='udp')
           dut2.echoserver(addr2_s, proto='udp')

           dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
           dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
           peer1.lookup_for_failed_decompression()
           peer2.lookup_for_failed_decompression()
           dut1.stop_echoserver()
           dut2.stop_echoserver()

# Configure ROHC uncompressed profile
           peer1.rohc_add_profile(if_name1[:5], if_name1[5:], if_name1, '0', '2')
           peer1.rohc_shell_exit()
           peer2.rohc_add_profile(if_name2[:5], if_name2[5:], if_name2, '0', '2')
           peer2.rohc_shell_exit()

           if v6:
               peer1.host.send_and_return_all('ping6 -s 1000 -c 10  %s' % (addr2_c))
               peer2.host.send_and_return_all('ping6 -s 1000 -c 10 %s' % (addr1_c))
           else:
               peer1.host.send_and_return_all('ping -s 1000 -c 10 %s' % (addr2_c))
               peer2.host.send_and_return_all('ping -s 1000 -c 10 %s' % (addr1_c))

           peer1.lookup_for_failed_decompression()
           peer2.lookup_for_failed_decompression()

# Configure ROHC IP  profile
           peer1.rohc_add_profile(if_name1[:5], if_name1[5:], if_name1, '4', '2')
           peer1.rohc_shell_exit()
           peer2.rohc_add_profile(if_name2[:5], if_name2[5:], if_name2, '4', '2')
           peer2.rohc_shell_exit()

           if v6:
               peer1.host.send_and_return_all('ping6 -s 1000 -c 10 %s' % (addr2_c))
               peer2.host.send_and_return_all('ping6 -s 1000 -c 10 %s' % (addr1_c))
           else:
               peer1.host.send_and_return_all('ping -s 1000 -c 10 %s' % (addr2_c))
               peer2.host.send_and_return_all('ping -s 1000 -c 10 %s' % (addr1_c))

           peer1.lookup_for_failed_decompression()
           peer2.lookup_for_failed_decompression()


######## Delete profiles ########

# Delete ROHC IP profile
           peer1.rohc_del_profile(if_name1[:5], if_name1[5:], if_name1, '4', '2')
           peer1.rohc_shell_exit()
           peer2.rohc_del_profile(if_name2[:5], if_name2[5:], if_name2, '4', '2')
           peer2.rohc_shell_exit()

#          Should be compressed by uncompressed profile 
           if v6:
               peer1.host.send_and_return_all('ping6 -s 1000 -c 2 %s' % (addr2_c))
               peer2.host.send_and_return_all('ping6 -s 1000 -c 2 %s' % (addr1_c))
           else:
               peer1.host.send_and_return_all('ping -s 1000 -c 2 %s' % (addr2_c))
               peer2.host.send_and_return_all('ping -s 1000 -c 2 %s' % (addr1_c))

           peer1.lookup_for_failed_decompression()
           peer2.lookup_for_failed_decompression()
#        print "IP profile deleted"

# Delete ROHC uncompressed profile
           peer1.rohc_del_profile(if_name1[:5], if_name1[5:], if_name1, '0', '2')
           peer1.rohc_shell_exit()
           peer2.rohc_del_profile(if_name2[:5], if_name2[5:], if_name2, '0', '2')
           peer2.rohc_shell_exit()

# UDP and TCP compression should work 
           if v6:
               dut1.echoserver(addr1_s, proto='tcp')
               dut2.echoserver(addr2_s, proto='tcp')
           else:               
               dut1.echoserver(addr1_c, proto='tcp')
               dut2.echoserver(addr2_c, proto='tcp')

           dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)
           dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7303, verify_data=True, reuse_addr=True)
           peer1.lookup_for_failed_decompression()
           peer2.lookup_for_failed_decompression()
           dut1.stop_echoserver()
           dut2.stop_echoserver()

           dut1.echoserver(addr1_s, proto='udp')
           dut2.echoserver(addr2_s, proto='udp')
           dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
           dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
           peer1.lookup_for_failed_decompression()
           peer2.lookup_for_failed_decompression()
           dut1.stop_echoserver()
           dut2.stop_echoserver()
#          print "Uncompressed profile deleted"


# Delete UDP profile
           peer1.rohc_del_profile(if_name1[:5], if_name1[5:], if_name1, '2', '2')
           peer1.rohc_shell_exit()
           peer2.rohc_del_profile(if_name2[:5], if_name2[5:], if_name2, '2', '2')
           peer2.rohc_shell_exit()

#          TCP compression should work 
           if v6:
               dut1.echoserver(addr1_s, proto='tcp')
               dut2.echoserver(addr2_s, proto='tcp')
           else:               
               dut1.echoserver(addr1_c, proto='tcp')
               dut2.echoserver(addr2_c, proto='tcp')

           dut1.echoclient(addr2_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
           dut2.echoclient(addr1_c, proto='tcp', nbuf = 100, chunk_size = 100, local_port = 7304, verify_data=True, reuse_addr=True)
           peer1.lookup_for_failed_decompression()
           peer2.lookup_for_failed_decompression()
           dut1.stop_echoserver()
           dut2.stop_echoserver()
#          print "ROHC UDP profile deleted"

# Delete TCP profile
           peer1.rohc_del_profile(if_name1[:5], if_name1[5:], if_name1, '6', '2')
           peer1.rohc_shell_exit()
           peer2.rohc_del_profile(if_name2[:5], if_name2[5:], if_name2, '6', '2')
           peer2.rohc_shell_exit()
#          print "TCP profile deleted"

        internal()

# Delete interface
        peer1.rohc_del_if(if_name1[:5], if_name1[5:])
        peer1.rohc_shell_exit()
        peer2.rohc_del_if(if_name2[:5], if_name2[5:])
        peer2.rohc_shell_exit()
#       print "Interface deleted"

        internal()

# Clean up the ROHC
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()


############################################################
class hop_dst_opt_pppoe:
    'Test ROHC IP: Test hop by hop, dst options'
    def config(self):
        self.hosts = 3
        self.v6 = True
        self.v4 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts[0].ipcom_shell(), hosts[1].ipcom_shell()

# Configure PPPoE and ROHC
        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6)
        addr = addr2_c

        def internal(c,s):
            for is_on in False, True:
                _sport = s.alloc_port()
                if is_on:
                    log("Test closedown when linger is set to 1 second")
                else:
                    log("Test closedown when linger is off")

                ssock = s.socket('inet'+v6, 'stream', 'tcp')
                ssock.setsockopt('ipv6', 'dstopt', 1)
                ssock.setsockopt('ipv6', 'hopopt', 1)
                ssock.bind(port = _sport)
                ssock.listen()

                csock = c.socket('inet'+v6, 'stream', 'tcp')
                csock.getsockopt('socket', 'linger', exp_data = 'off')

                if is_on:
                    csock.setsockopt('socket', 'linger', 0)

                pkt_num = 100

                csock.connect(addr, _sport)
                asock = ssock.accept()
                send_pkts(csock, asock, pkt_num)

                p = 'ipv6'
                opt_v = 'nop'

                o = 'dstopt'
                csock.setsockopt(p, o, opt_v)
                asock.setsockopt(p, o, 1)
                send_pkts(csock, asock, pkt_num)

                o = 'hopopt'
                csock.setsockopt(p, o, opt_v)
                asock.setsockopt(p, o, 1)
                send_pkts(csock, asock, pkt_num)

                ssock.close()
                csock.close()
                asock.close()
        internal(c,s)
# Swap  PPPoE addresses
        addr = addr1_c
        internal(s,c)
# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)


############################################################
class iprohc_rth_type0_opt:
    'Test IPv6 RTH type 0 header compression - TCP profile'
    def config(self):
        self.hosts = 3
        self.v6 = True
        self.v4 = False

    def test(self, log, hosts, v6, _):
#       client, server, intermediate nodes 
#       Don't change the order of the nodes 
        c, i, s = hosts[0].ipcom_shell(), hosts[1].ipcom_shell(), hosts[2].ipcom_shell()
        c_h, i_h, s_h = hosts
        peer_c = rohc_base(c_h)
        peer_i = rohc_base(i_h)

        c_addr = c.alloc_ip(v6, net = 253)
        s_addr = s.alloc_ip(v6)
        i_addr = i.alloc_ip(v6, net = 253)
 
        s_netif = s.netif()
        s_netif.add_ip(s_addr)
        addr = s_addr

        c_vlan = c_h.add_vlan(c_addr, vlan= 'new')
        i_vlan = i_h.add_vlan(i_addr, vlan= c_vlan.id)

        _sport = s.alloc_port()
        ssock = s.socket('inet'+v6, 'stream', 'tcp')
        ssock.bind(port = _sport)
        ssock.listen()

        csock = c.socket('inet'+v6, 'stream', 'tcp')

        pkt_num = 200

        csock.connect(addr, _sport)
        asock = ssock.accept()
        send_pkts(csock, asock, pkt_num)
        time.sleep(1)

        c.set_sysvar('iprohc.large_cid', 0)
        i.set_sysvar('iprohc.large_cid', 0)

        ifname = 'vlan%s' % (c_vlan.id)
        peer_c.rohc_configure('vlan', c_vlan.id, ifname, '6', '1')  
        peer_i.rohc_configure('vlan', c_vlan.id, ifname, '6', '1')

        p = 'ipv6'
        o = 'rthdropt'
        opt_v = '%s' % (i_addr)

        csock.setsockopt(p, o, opt_v)
        send_pkts(csock, asock, pkt_num)
        peer_i.lookup_for_failed_decompression()

        peer_c.rohc_shell_start()
        peer_c.rohc_close()
        peer_c.rohc_shell_exit()
        peer_i.rohc_shell_start()
        peer_i.rohc_close()
        peer_i.rohc_shell_exit()

        c_vlan.destroy()
        i_vlan.destroy()

        csock.close()
        asock.close()
        ssock.close()

        return


############################################################
class rth_type0_opt:
    'Test IPv6 RTH type 0 sticky option without rohc'
    def config(self):
        self.hosts = 3
        self.v6 = True
        self.v4 = False

    def test(self, log, hosts, v6, _):
#       client, server, intermediate nodes 
        c, s, i = hosts[0].ipcom_shell(), hosts[1].ipcom_shell(), hosts[2].ipcom_shell()

        c_addr = c.alloc_ip(v6)   
        s_addr = s.alloc_ip(v6) 
        i_addr = i.alloc_ip(v6)
      
        c_netif = c.netif()
        s_netif = s.netif()
        i_netif = i.netif()

        c_netif.add_ip(c_addr)
        s_netif.add_ip(s_addr)
        i_netif.add_ip(i_addr)

        addr = s_addr

        _sport = s.alloc_port()
        ssock = s.socket('inet'+v6, 'stream', 'tcp')
        ssock.bind(port = _sport)
        ssock.listen()

        csock = c.socket('inet'+v6, 'stream', 'tcp')

        pkt_num = 5

        csock.connect(addr, _sport)
        asock = ssock.accept()
        send_pkts(csock, asock, pkt_num)
                                 
        p = 'ipv6'
        o = 'rthdropt'

        opt_v = '%s' % (i_addr)
        csock.setsockopt(p, o, opt_v)
        send_pkts(csock, asock, pkt_num)

        opt_v = '%s%s' % (i_addr,',')
        csock.setsockopt(p, o, opt_v)
        send_pkts(csock, asock, pkt_num)

        opt_v = '%s%s%s' % (i_addr,',', i_addr,)
        csock.setsockopt(p, o, opt_v)
        send_pkts(csock, asock, pkt_num)

        opt_v = '%s%s%s%s%s' % (i_addr,',',i_addr, ',',i_addr)
        csock.setsockopt(p, o, opt_v)
        send_pkts(csock, asock, pkt_num)

        opt_v = '%s%s%s%s%s' % (i_addr,',', i_addr,',','123234345')
        csock.setsockopt(p, o, opt_v)

        send_pkts(csock, asock, pkt_num)
        csock.close()
        asock.close()
        ssock.close()

        return
