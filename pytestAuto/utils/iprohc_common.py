#############################################################################
#
# Copyright (c) 2006-2013,2018 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

import re
import time
# import pdb

from pppoe import PPPOEServer, PPPOEClient
import sys


from utils.log_record import log


class RohcBase(object):
    rohc_is_shell = False

    def __init__(self, host):
        self.host = host
        self.rohc_prompt = 'rohc>'
        self.shell = 'rohc'
        self.vxprompt = '# '

    def rohc_exit(self):  # xiaozhan, modify
        self.host.sendAndExpect("exit", self.vxprompt)

        # set rohc environment variable  # xiaozhan, debug

    def rohc_env_set(self, var, value):
        self.host.set_sysvar(var, value)

    def rohc_shell_start(self):
        if self.rohc_is_shell is False:
            # self.prompt_org = self.host.cmdPrompt   # xiaozhan, modify
            self.host.sendAndExpect(self.shell, self.rohc_prompt)
            time.sleep(1)
            self.rohc_is_shell = True

    def rohc_shell_exit(self):
        # exit rohc shell
        if self.rohc_is_shell is True:
            self.host.sendAndExpect('exit', self.vxprompt)  # xiaozhan modify
            self.rohc_is_shell = False

    def rohc_close(self):
        ret = self.host.sendAndReturnAll('close', self.rohc_prompt)
        time.sleep(1)

        for line in ret:
            m = re.match(r'(ROHC is closed)|(Failed to close ROHC)', line)
            if m:
                break
            else:
                raise RohcException('Rohc can not be closed')

    def rohc_open(self):
        ret = self.host.sendAndReturnAll('open', self.rohc_prompt)
        time.sleep(2)
        for line in ret:
            m = re.match(r'(ROHC is opened)|(Failed to open ROHC, ret -1)', line)
            if m:
                break
            else:
                raise RohcException('ROHC can not be started')

    def rohc_configure(self, interface_name, interface_num, interface, profile, cid_val):
        self.rohc_shell_start()
        self.rohc_close()
        time.sleep(1)
        self.rohc_open()
        time.sleep(1)
        self.host.sendAndExpect('ifadd -ifname %s -ifnum %s' % (interface_name, interface_num), self.rohc_prompt)
        self.host.sendAndExpect('ifprofileadd -ifname %s -profileid %s;' % (interface, profile), self.rohc_prompt)
        self.host.sendAndExpect('compcidmod -ifname %s -profileid %s -cid %s;' % (interface, profile, cid_val),
                                self.rohc_prompt)

    def rohc_add_if(self, interface_name, interface_num):
        # self.rohc_prompt = 'rohc>'
        self.rohc_shell_start()
        lines = self.host.sendAndReturnAll('ifadd -ifname %s -ifnum %s' % (interface_name, interface_num),
                                           self.rohc_prompt)
        return lines

    def rohc_del_if(self, interface_name, interface_num):
        # self.rohc_prompt = 'rohc>'
        self.rohc_shell_start()
        lines = self.host.sendAndReturnAll('ifdel -ifname %s -ifnum %s' % (interface_name, interface_num),
                                           self.rohc_prompt)
        return lines

    def rohc_add_profile(self, interface_name, interface_num, interface, profile, cid_val):
        # self.rohc_prompt = 'rohc>'
        self.rohc_shell_start()
        lines = self.host.sendAndReturnAll('ifprofileadd -ifname %s -profileid %s;' % (interface, profile),
                                           self.rohc_prompt)
        return lines

    def rohc_del_profile(self, interface_name, interface_num, interface, profile, cid_val):
        #       self.rohc_prompt = 'rohc>'
        self.rohc_shell_start()
        lines = self.host.sendAndReturnAll('ifprofiledel -ifname %s -profileid %s;' % (interface, profile),
                                           self.rohc_prompt)
        return lines

    def rohc_cleanup(self):
        self.rohc_close()
        self.rohc_shell_exit()

    def if_config(self, interface, addr, v6):
        if v6:
            self.host.sendAndExpect('ifconfig %s inet6 add %s up' % (interface, addr), self.vxprompt)
        else:
            self.host.sendAndExpect('ifconfig %s inet add %s up' % (interface, addr), self.vxprompt)

    def get_eth_names(self):
        lines = self.host.sendAndReturnAll('ifconfig -a', self.vxprompt)
        return lines

    def if_detach(self, if_name):
        self.host.sendAndExpect('ifconfig %s down' % if_name, self.vxprompt)
        self.host.sendAndExpect('ifconfig %s detach' % if_name, self.vxprompt)

    def rohc_show(self):
        self.rohc_shell_start()
        lines = self.host.sendAndReturnAll('rohcshow', self.rohc_prompt)
        self.rohc_shell_exit()
        return lines

    def lookup_for_failed_decompression(self):
        self.rohc_shell_start()
        lines = self.rohc_show()
        lines_len = len(lines)
        ret = "num_failed:"
        pos = 0
        count = 0
        for y in range(pos, lines_len):
            line = lines[y]
            s = line.find(ret)
            if s >= 0:
                l = line.split()
                if l[1] > '1':
                    raise RohcException('ROHC lookup_for_failed_decompression failed')
                count = count + 1
        if count == 0:
            raise RohcException('ROHC lookup_for_failed_decompression failed')


def config_pppoe(hosts, peer1, peer2, vxprompt, version):  # TODO xiaozhan,need to debug v6
    # Configure PPPoE
    c, s, p = hosts

    c.sendAndExpect('sysvar set -co ipppp.pppoe.max_eth_sessions "30"', vxprompt)
    c.sendAndExpect('sysvar set -co ipppp.pppoe.max_sessions "30"', vxprompt)
    s.sendAndExpect('sysvar set -co ipppp.pppoe.max_eth_sessions "30"', vxprompt)
    s.sendAndExpect('sysvar set -co ipppp.pppoe.max_sessions "30"', vxprompt)
    p.sendAndExpect('sysvar set -co ipppp.pppoe.max_eth_sessions "30"', vxprompt)
    p.sendAndExpect('sysvar set -co ipppp.pppoe.max_sessions "30"', vxprompt)

    server = PPPOEServer(s, p, version)  # TODO xiaozhan
    client = PPPOEClient(c, server, version)  # TODO  xiaozhan

    # Configure local address
    server.negotiate()
    server.chap()

    client.negotiate()
    # client.credentials() 
    client.credentials(user="ftp", password="interpeak")
    client.chap()

    # Create interface
    client.create()

    addr1_1 = client.pppoe_local._addrstr
    addr2_2 = client.pppoe_peer._addrstr

    lines = peer1.get_eth_names()
    lines_len = len(lines)

    ppp_found = False
    for y in range(0, lines_len):
        line = lines[y]
        s = line.find('Link type:PPP over Ethernet')
        if s >= 0:
            # Check the interface name
            l = line.split()
            if_name1 = l[0]
            if if_name1.find('pppoe') == -1:
                raise RohcException('No PPPoE interface found')

            # Check the interface address
            for x in range(y, y + 5):
                l_next = lines[x]
                if l_next.find(addr1_1) >= 0:
                    ppp_found = True
                    break

    if not ppp_found:
        raise RohcException('No PPPoE interface found')

    lines = peer2.get_eth_names()
    lines_len = len(lines)
    ppp_found = False
    for y in range(0, lines_len):
        line = lines[y]
        s = line.find('Link type:PPP over Ethernet')
        if s >= 0:
            # Check the interface name
            l = line.split()
            if_name2 = l[0]
            if if_name2.find('pppoe') == -1:
                raise RohcException('No PPPoE interface found')

            # Check the interface address
            for x in range(y, y + 5):
                l_next = lines[x]
                if l_next.find(addr2_2) == -1:
                    ppp_found = True
                    break
    if not ppp_found:
        raise RohcException('No PPPoE interface found')
    return addr1_1, addr2_2, if_name1, if_name2


def pppoe_addr(addr1_1, addr2_2, if_name1, if_name2, version):
    #   if v6:
    addr1 = "%s%%%s" % (addr1_1, if_name1)
    addr11 = "%s%%%s" % (addr1_1, if_name2)

    #   if v6:
    addr2 = "%s%%%s" % (addr2_2, if_name2)
    addr22 = "%s%%%s" % (addr2_2, if_name1)
    return addr1, addr11, addr2, addr22


def lookup_in_lines(lines, ret, pos, must_be):
    lines_len = len(lines)
    found = False
    for y in range(pos, lines_len):
        line = lines[y]
        s = line.find(ret)
        if s >= 0:
            found = True
            break

    if found:
        if must_be is False:
            log.info('ret is---', ret)
            raise RohcException('ROHC lookup_in_lines failed')
    else:
        if must_be is True:
            log.info('ret is---', ret)
            raise RohcException('ROHC lookup_in_lines failed')

    return y


class RohcException(Exception):
    pass


def validate_and_cleanup_rohc(hosts):
    peer1 = RohcBase(hosts[0])
    peer2 = RohcBase(hosts[1])

    peer1.lookup_for_failed_decompression()
    peer2.lookup_for_failed_decompression()

    # Clean up the ROHC
    peer1.rohc_shell_start()
    peer1.rohc_close()
    peer1.rohc_shell_exit()
    peer2.rohc_shell_start()
    peer2.rohc_close()
    peer2.rohc_shell_exit()


def test_setup(log, type, nut1, nut2, addr1, addr2, tunnel_net, v6='', treat_as_ppp=True):
    tunnel_addrs = (nut1.alloc_ip(v6=v6, net=tunnel_net),
                    nut2.alloc_ip(v6=v6, net=tunnel_net))

    tunnel_ifs = (nut1.add_netif(addr=tunnel_addrs[0],
                                 tunnel=type,
                                 tunnel_local_ip=addr1,
                                 tunnel_remote_ip=addr2),
                  nut2.add_netif(addr=tunnel_addrs[1],
                                 tunnel=type,
                                 tunnel_local_ip=addr2,
                                 tunnel_remote_ip=addr1))

    if treat_as_ppp:
        nut1.send_and_return_all('ifconfig %s inet dstaddr %s'
                                 % (tunnel_ifs[0].ifname, tunnel_addrs[1].addr))
        nut2.send_and_return_all('ifconfig %s inet dstaddr %s'
                                 % (tunnel_ifs[1].ifname, tunnel_addrs[0].addr))

    return tunnel_addrs[0], tunnel_addrs[1], tunnel_ifs


def config_pppoe_rohc(hosts, vxprompt, v6, profile=2):  # xiaozhan modify
    peer1 = RohcBase(hosts[0])
    peer2 = RohcBase(hosts[1])
    s, c = hosts[0], hosts[1]

    # small CID
    s.sendAndExpect('sysvar set -co iprohc.large_cid "1"', vxprompt)
    c.sendAndExpect('sysvar set -co iprohc.large_cid "1"', vxprompt)
    s.sendAndExpect('sysvar set -co iprohc.max_cid "50"', vxprompt)
    c.sendAndExpect('sysvar set -co iprohc.max_cid "50"', vxprompt)

    # Configure PPPoE
    addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, vxprompt, v6=v6)

    # Prepare PPPoE addresses for use
    addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

    # This code can be reviewed after activation of the uncompressed  profile to send uncompressed packets.
    # The stack might need to negotiate with neighbor nodes when echo-client is invoked.
    # These ping operations ensure that ROHC is not configured before such messaging.
    # --start--
    if v6:  # xiaozhan modify
        peer1.host.sendAndExpect('ping6 -s 1000 %s' % addr2_c, vxprompt)
        peer2.host.sendAndExpect('ping6 -s 1000 %s' % addr1_c, vxprompt)
    else:
        peer1.host.sendAndExpect('ping -s 1000 %s' % addr2_c, vxprompt)
        peer2.host.sendAndExpect('ping -s 1000 %s' % addr1_c, vxprompt)

    time.sleep(1)
    # --end--

    # Configure ROHC
    peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, profile, '1')
    peer1.rohc_shell_exit()
    peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, profile, '1')
    peer2.rohc_shell_exit()

    return addr1_c, addr2_c, addr1_s, addr2_s
