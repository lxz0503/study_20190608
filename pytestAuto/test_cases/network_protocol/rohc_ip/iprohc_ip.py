#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


#import pdb

from pytestAuto.utils.iprohc_common import *
#from tcp import validate_and_cleanup_rohc, test_setup
from tunnel import _has_ipv6_support

############################################################
class small_cid:
    'Test IP profile with small CID'
    def config(self):
        self.hosts = 3
        self.eta = 30 
    def test(self, log, hosts, v6, _):
        log('Rohc IP profile test: small_cid', echo=True)
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

# Configure ROHC 
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '4', '1')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '4', '1')
        peer2.rohc_shell_exit()

# Begin testing  
# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions     
        dut1.echoserver(addr1_s, proto='udp')
        dut2.echoserver(addr2_s, proto='udp')
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr2, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Validate test results
# lookup_in_lines usage example 
#        lines = peer1.rohc_show()
# Search for the 1st occurrence
#        pos = lookup_in_lines(lines, "num_failed:    0", 0, True)
# Search for the next occurrence 
#        pos = lookup_in_lines(lines, "num_failed:    0", pos + 1, False)

# Search for failed decompression 
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

        dut1.stop_echoserver()
        dut2.stop_echoserver()

# This profile could be tested with 2 interfaces. But  this will require 2 PPP connection   
#        dut1.echoserver(addr1_1, proto='udp')
#        dut2.echoserver(addr2_2, proto='udp')
#        dut1.echoclient(addr2_2, proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1_1, proto='udp', nbuf = 100, chunk_size = 49, local_port = 7302, verify_data=True)
#        dut1.echoclient(addr2_2, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1_1, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)

# Clean up the ROHC  
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()                 
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

        dut1.stop_echoserver()
        dut2.stop_echoserver()


############################################################
class large_cid:
    'Test IP profile with large CID and large CID value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc IP profile test: large_cid', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()
        
        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6 = v6)

# Prepare PPPoE addresses for use
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)
                     
# Larg CID
        dut1.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '5000')
        dut2.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.max_cid', '5000')

#Configure ROHC 
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '4', '2000')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '4', '2000')
        peer2.rohc_shell_exit()

# Begin testing
        dut1.echoserver(addr1_s, proto='udp')
        dut2.echoserver(addr2_s, proto='udp')

# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr22, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr11, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

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
    'Test IP profile with large CID and small value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc IP profile test: large_cid_small_val', echo=True)
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

#Configure ROHC
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '4', '2')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '4', '2')
        peer2.rohc_shell_exit()

# Begin testing
        dut1.echoserver(addr1_s, proto='udp')
        dut2.echoserver(addr2_s, proto='udp')

# Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr2, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

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
class mine_enc_pppoe:
    "ROHC IP: Mine encapsulation test (GRE)"
    def config(self):
        self.hosts = 3
        self.eta = 6
        self.v6 = False
        self.works_on_iplite = False
        self.works_on_gpp = False

    def test(self, log,  hosts, v6, _):
        def wait_tcp_ready(host, timeout=80):
            # wait tcp ready or S_errno_EADDRINUSE happens
            start_time = time.time()
            i = 0
            
            while True:
                if (time.time() - start_time) >= timeout:
                    print '=== wait_tcp_ ready() timeout after %s seconds' % timeout
                    break

                lines = host.shops.send_and_return_all("netstat -P")
                if ('\n'.join(lines).find('TIME_WAIT') != -1):
                        time.sleep(1)
                        i += 1
                else:
                    break

                        
        nut1, nut2, nut3 = hosts

# Configure PPPoE and ROHC
        dut1  = nut1.ipcom_shell()
        dut2  = nut2.ipcom_shell()

        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6, 4)
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
        wait_tcp_ready(nut1)
        dut1.echoclient(addr2, proto='tcp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#       dut1.echoclient(addr2, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)
#       dut2.echoclient(addr1, proto='tcp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True, reuse_addr=True)


# Test 2 connections with the same destination port
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 1100, local_port = 7305, verify_data=True, reuse_addr=True)

# Test 2 connections with the same source ports
# Between ports 7302/7301 in both directions
        wait_tcp_ready(nut1)
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True, reuse_addr=True)
        wait_tcp_ready(nut2)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 1100, local_port = 7304, verify_data=True, reuse_addr=True)
        dut1.stop_echoserver()
        dut2.stop_echoserver()
        dut1.echoserver(addr1, proto='tcp', port = 7307)
        dut2.echoserver(addr2 ,proto='tcp', port = 7307)
        dut1.echoclient(addr2, proto='tcp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='tcp', nbuf = 20, chunk_size = 1100, local_port = 7304, port = 7307, verify_data=True, reuse_addr=True)

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)

        dut1.stop_echoserver()
        dut2.stop_echoserver()

        for t in tunnel_ifs:
           t.destroy()

        return


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
        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6, 4)
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

                pkt_num = 5

                csock.connect(addr, _sport)
                asock = ssock.accept()
                send_pkts(csock, asock, pkt_num, '')

                p = 'ipv6'
                opt_v = 'nop'

                o = 'dstopt'
                csock.setsockopt(p, o, opt_v)
                asock.setsockopt(p, o, 1)
                send_pkts(csock, asock, pkt_num, '')

                o = 'hopopt'
                csock.setsockopt(p, o, opt_v)
                asock.setsockopt(p, o, 1)
                send_pkts(csock, asock, pkt_num, '')

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
def send_pkts(csock, asock, num_pkts, anc_data):
     data = "*012345678901234567890123456789012345678901234567890123456789!"
     data_len = len(data)
     i = 1
     while i <=  num_pkts:
        i += 1
        csock.send(data, ancillary_data=anc_data)
        asock.recv(exp_len = data_len)


############################################################
class ipip_pppoe:
    "ROHC IPIP: Test Ipv4 over IPv4 compression"
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

        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6, 4)
        addr1, addr2, tunnel_ifs  = test_setup(log, "ip", nut1, nut2, addr1_c, addr2_c, 17, v6)

# Begin testing
        dut1.echoserver(addr1, proto='udp')
        dut2.echoserver(addr2, proto='udp')

# Test a connection for short packets
# Between ports 7302/7301 in both directions
        dut1.echoclient(addr2, proto='udp', nbuf = 1, chunk_size = 100, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='udp', nbuf = 100, chunk_size = 1, local_port = 7302, verify_data=True, reuse_addr=True)

# Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
# Between ports 7302/7301 in both directions
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
class ip6_ip4_pppoe:
    "ROHC IPv6 over IPv4: Test IPv6 over IPv4 compression"
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

        addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, v6, 4)

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

        dut1.echoserver(addr1, proto='udp')
        dut2.echoserver(addr2, proto='udp')

        dut1.echoclient(addr2, proto='udp', nbuf = 100, chunk_size = 1000, local_port = 7302, verify_data=True, reuse_addr=True)
        dut2.echoclient(addr1, proto='udp', nbuf = 100, chunk_size = 1000, local_port = 7302, verify_data=True, reuse_addr=True)

# Validate and celan up ROHC
        validate_and_cleanup_rohc(hosts)

        dut1.stop_echoserver()
        dut2.stop_echoserver()

        for t in tunnel_ifs:
            t.destroy()


############################################################
class iprohc_rth_type0_opt:
    'Test IPv6 RTH type 0 header compression - IP profile'
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

        peer_c.host.send_and_return_all('ping6 -s 10 %s' % (i_addr))
        peer_i.host.send_and_return_all('ping6 -s 10 %s' % (c_addr))

        _sport = s.alloc_port()
        ssock = s.socket('inet'+v6, 'stream', 'tcp')
        ssock.bind(port = _sport)
        ssock.listen()

        csock = c.socket('inet'+v6, 'stream', 'tcp')

        pkt_num = 200

        csock.connect(addr, _sport)
        asock = ssock.accept()
        send_pkts(csock, asock, pkt_num, '')
        time.sleep(1)

        c.set_sysvar('iprohc.large_cid', 0)
        i.set_sysvar('iprohc.large_cid', 0)

        ifname = 'vlan%s' % (c_vlan.id)
        peer_c.rohc_configure('vlan', c_vlan.id, ifname, '4', '1')
        peer_i.rohc_configure('vlan', c_vlan.id, ifname, '4', '1')

        p = 'ipv6'
        o = 'rthdropt'
        opt_v = '%s' % (i_addr)

        csock.setsockopt(p, o, opt_v)
        send_pkts(csock, asock, pkt_num, '')
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

