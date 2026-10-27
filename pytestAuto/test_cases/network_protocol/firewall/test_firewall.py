#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:2/26/2024 4:06 PM
@file:test_firewall.py
"""
import pytest
import allure
import sys
import config
import time
import pexpect

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from test_cases.network_protocol.firewall.boot_qemu import BootQemu
from utils.util import IF
from utils.util import layout_net
from utils.util import abnet
from utils.util import abnet6

'Firewall IP Filter'

############################ Network layout ####################################
#
#                                  10.ln.2.1
#                                  2000:ln::10.ln.2.1
#     ------------              -----------              ------------
#    |            |            |           |            |            |
#    |  PRIVATE   |------------| FIREWALL  |------------|  PUBLIC    |
#    |   (c)      |            |   (r)     |            |   (s)      |
#    |            |            |           |            |            |
#     ------------              -----------              ------------
#     10.ln.1.1                10.ln.1.3                10.ln.2.3
#     2000:ln::10.ln.1.1       2000:ln::10.ln.1.3       2000:ln::10.ln.2.3
#         z                         x                         y
#
#    n.r                   #router
#    n.s                   #server
#    n.c                   #client 1
#    n.rifc = rifc         #router netif facing client
#    n.rifs = rifs         #router netif facing server
#    n.ripc = ripc         #router ip on netif facing client
#    n.rips = rips         #router ip on netif facing server
#
################################################################################

dstport = 30000
srcport = 40000
natport = 50000


################################################################################
#        check_mtu - make sure mtu setting is correct
################################################################################
def check_mtu(n):
    n.r.send(n.r.las_prefix() + "ifconfig %s" % n.rifc.ifname)
    i = n.r.expect_exact_and_wait_prompt(['MTU:1496', 'MTU:1492'])
    if i == 1:
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ifconfig %s mtu 1496" % n.rifc.ifname)
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ifconfig %s mtu 1496" % n.rifs.ifname)
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ifconfig -a")


################################################################################
#        echo - Test UDP, TCP or RAW through firewall using echo client/server
################################################################################
def echo(n, dstport, srcport, protocol, v6, succeed=True, count=1,
         chunk_size=1024, connection_refused=False, network_unreachable=False):
    for _ in range(count):
        time.sleep(0.3)
        n.sshell.echoserver(proto=protocol, port=dstport)
        n.cshell.echoclient(n.s.ip().addr, verify_data=True,
                            reuse_addr=True, proto=protocol, nbuf=1,
                            chunk_size=chunk_size, local_port=srcport, port=dstport,
                            succeed=succeed, connection_refused=connection_refused,
                            network_unreachable=network_unreachable)
        n.sshell.stop_echoserver()


################################################################################
#        echo_ipsec
################################################################################
def echo_ipsec(n, dstport, srcport, protocol, v6, succeed=True, count=1,
               chunk_size=1024, connection_refused=False, network_unreachable=False):
    for _ in range(count):
        time.sleep(0.3)
        n.rshell.echoserver(proto=protocol, port=dstport)
        n.sshell.echoclient(n.rips.addr, verify_data=True,
                            reuse_addr=True, proto=protocol, nbuf=1,
                            chunk_size=chunk_size, local_port=srcport, port=dstport,
                            succeed=succeed, connection_refused=connection_refused,
                            network_unreachable=network_unreachable)
        n.rshell.stop_echoserver()


################################################################################
#        add_proto - Test various protocols through NAT
################################################################################
def add_ruleset(n, ruleset, v6, mac=False):
    # disable firewall
    # flush old rules, states and log entries
    # clear statistics
    # add the rules in the ruleset
    # enable firewall

    n.r.send(n.r.las_prefix() + "keyadm flush")
    n.r.wait_prompt()
    n.s.send(n.s.las_prefix() + "keyadm flush")
    n.s.wait_prompt()
    n.c.send(n.c.las_prefix() + "keyadm flush")
    n.c.wait_prompt()

    n.r.send(n.r.las_prefix() + "ipf -D")
    n.r.wait_prompt()
    n.r.expect_prompt(n.r.las_prefix() + "ipf -m -Frls")
    n.r.expect_prompt(n.r.las_prefix() + "ipf -Frls")
    n.r.expect_prompt(n.r.las_prefix() + "ipf -Z")
    for rule in ruleset:
        if mac:
            rule = "ipf -m " + " ".join(rule)
        elif v6:
            rule = "ipf -6 " + " ".join(rule)
        else:
            rule = "ipf " + " ".join(rule)
        n.r.expect_prompt(n.r.las_prefix() + rule)
    if mac:
        n.r.send(n.r.las_prefix() + "ipf -m -Pr")  # print the MAC rules
    else:
        n.r.send(n.r.las_prefix() + "ipf -Pr")  # print the rules
    n.r.wait_prompt()
    n.r.send(n.r.las_prefix() + "ipf -E")
    n.r.wait_prompt()


################################################################################
#        start_apache - Start apache
################################################################################
def start_apache(n):
    # make sure the firewall is diabled
    n.r.send(n.r.las_prefix() + "ipf -D")
    n.r.wait_prompt()

    for _ in range(5):
        try:
            # stop apache first
            n.s.send_and_wait_prompt("/etc/init.d/apache2 stop")
            time.sleep(4)
            n.s.send_and_wait_prompt("pkill -9 apache2")
            time.sleep(4)

            # start apache
            n.s.send_and_wait_prompt("/etc/init.d/apache2 start")
            time.sleep(4)

            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo=False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.otherwebsite.com\n' +
                     'Connection: close\n',
                     sudo=False)
            n.c.expect_exact('HTTP/1.1 200 OK')
            n.c.expect_exact('This is the HTTP URL filter test page')
            n.c.expect_exact('Connection closed by foreign host')
            n.c.wait_prompt()
            break

        except pexpect.TIMEOUT:
            n.s.send_and_wait_prompt('netstat -ant')
            n.s.send_and_wait_prompt('ps -auxww')
            pass

    n.s.send_and_wait_prompt('netstat -ant')
    n.s.send_and_wait_prompt('ps -auxww')


class TestFirewall(BootQemu):
    v6 = '6'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_firewall_syntax(self, version):
        """
         Verify IP filter rule syntax.
         Pass/Fail criteria: It must be possible to add all example IP filter rules
         from the manual without any errors both with the shell command and from a rule file.
        """
        with allure.step(f'Verify IP filter rule syntax'):
            hosts = [self.t1, self.t2, self.t3]
            n = layout_net('rcs' + self.v6, hosts)

            # Check that the ipf command is available
            ret = n.r.sendAndReturnAll('ipf', self.vxprompt)
            assert 'firewall configuration' in ret
            n.r.sendAndExpect("ipf -V")


