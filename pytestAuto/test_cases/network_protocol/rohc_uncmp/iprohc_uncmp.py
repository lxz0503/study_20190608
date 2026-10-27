#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


from util import IF
from iprohc_common import *


############################################################
class small_cid:
    'Test uncompressed profile with small CID'
    def config(self):
        self.hosts = 3
        self.eta = 30 
    def test(self, log, hosts, v6, _):
	log('Rohc uncompressed profile test: small_cid', echo=True)
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

# The stack might need to negotiate with neighbor nodes when echo-client is invoked.
# These ping operations ensure that ROHC is not configured before such messaging.
#--start--
        if v6:
           peer1.host.send_and_return_all('ping6 -s 10 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping6 -s 10 %s' % (addr1_c))
        else:
           peer1.host.send_and_return_all('ping -s 10 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping -s 10 %s' % (addr1_c))
         
# Configure ROHC 
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '0', '1')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '0', '1')
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
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr2, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Search for failed decompression 
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

        dut1.stop_echoserver()
        dut2.stop_echoserver()

# Clean up the ROHC  
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()                 
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()


############################################################
class large_cid:
    'Test uncompressed profile with large CID and large CID value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc uncompressed profile test: large_cid', echo=True)
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
                     
# The stack might need to negotiate with neighbor nodes when echo-client is invoked.
# These ping operations ensure that ROHC is not configured before such messaging.
#--start--
        if v6:
           peer1.host.send_and_return_all('ping6 -s 10 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping6 -s 10 %s' % (addr1_c))
        else:
           peer1.host.send_and_return_all('ping -s 10 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping -s 10 %s' % (addr1_c))

# Larg CID
        dut1.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '5000')
        dut2.set_sysvar('iprohc.large_cid', '1')
        dut2.set_sysvar('iprohc.max_cid', '5000')

#Configure ROHC 
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '0', '2000')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '0', '2000')
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
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr22, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr11, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Search for failed decompression
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

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


############################################################
class large_cid_small_val:
    'Test uncompressed profile with large CID and small value'
    def config(self):
        self.hosts = 3
        self.eta = 15
    def test(self, log, hosts, v6, _):
        log('Rohc uncompressed profile test: large_cid_small_val', echo=True)
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

# The stack might need to negotiate with neighbor nodes when echo-client is invoked.
# These ping operations ensure that ROHC is not configured before such messaging.
#--start--
        if v6:
           peer1.host.send_and_return_all('ping6 -s 10 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping6 -s 10 %s' % (addr1_c))
        else:
           peer1.host.send_and_return_all('ping -s 10 %s' % (addr2_c))
           peer2.host.send_and_return_all('ping -s 10 %s' % (addr1_c))

#Configure ROHC
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '0', '2')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '0', '2')
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
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 100, chunk_size = 1100, local_port = 7302, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)
        dut2.echoclient(addr1_c, proto='udp', nbuf = 200, chunk_size = 100, local_port = 7302, verify_data=True)

# Test a connection. Generate 67000 packets to cause IP ID wraparound
# Between ports 7302/7301 in both directions
#        dut1.echoclient(addr2, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)
#        dut2.echoclient(addr1, proto='udp', nbuf = 67000,  chunk_size = 70, local_port = 7302, verify_data=True)

# Search for failed decompression
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

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

