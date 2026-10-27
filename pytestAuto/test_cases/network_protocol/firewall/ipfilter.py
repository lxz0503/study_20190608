#############################################################################
#
# Copyright (c) 2006-2013, 2017, 2020-2022 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

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

from util import IF
from util import layout_net
from util import abnet
from util import abnet6

import os
import config
import time
import pexpect

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
def echo(n, dstport, srcport, protocol, v6, succeed = True, count = 1,
         chunk_size = 1024, connection_refused = False, network_unreachable = False):

    for _ in range(count):
        time.sleep(0.3)
        n.sshell.echoserver(proto=protocol, port=dstport)
        n.cshell.echoclient(n.s.ip().addr, verify_data = True,
                            reuse_addr = True, proto = protocol, nbuf = 1,
                            chunk_size = chunk_size, local_port = srcport, port = dstport,
                            succeed = succeed, connection_refused = connection_refused,
                            network_unreachable = network_unreachable)
        n.sshell.stop_echoserver()

################################################################################
#        echo_ipsec
################################################################################
def echo_ipsec(n, dstport, srcport, protocol, v6, succeed = True, count = 1,
               chunk_size = 1024, connection_refused = False, network_unreachable = False):

    for _ in range(count):
        time.sleep(0.3)
        n.rshell.echoserver(proto=protocol, port=dstport)
        n.sshell.echoclient(n.rips.addr, verify_data = True,
                            reuse_addr = True, proto = protocol, nbuf = 1,
                            chunk_size = chunk_size, local_port = srcport, port = dstport,
                            succeed = succeed, connection_refused = connection_refused,
                            network_unreachable = network_unreachable)
        n.rshell.stop_echoserver()


################################################################################
#        add_proto - Test various protocols through NAT
################################################################################
def add_ruleset(n, ruleset, v6, mac = False):
    #disable firewall
    #flush old rules, states and log entries
    #clear statistics
    #add the rules in the ruleset
    #enable firewall

    n.r.send(n.r.las_prefix() +  "keyadm flush")
    n.r.wait_prompt()
    n.s.send(n.s.las_prefix() +  "keyadm flush")
    n.s.wait_prompt()
    n.c.send(n.c.las_prefix() +  "keyadm flush")
    n.c.wait_prompt()

    n.r.send(n.r.las_prefix() +  "ipf -D")
    n.r.wait_prompt()
    n.r.expect_prompt(n.r.las_prefix() +  "ipf -m -Frls")
    n.r.expect_prompt(n.r.las_prefix() +  "ipf -Frls")
    n.r.expect_prompt(n.r.las_prefix() +  "ipf -Z")
    for rule in ruleset:
        if mac:
            rule = "ipf -m " + " ".join(rule)
        elif v6:
            rule = "ipf -6 " + " ".join(rule)
        else:
            rule = "ipf " + " ".join(rule)
        n.r.expect_prompt(n.r.las_prefix() + rule)
    if mac:
        n.r.send(n.r.las_prefix() +  "ipf -m -Pr") #print the MAC rules
    else:
        n.r.send(n.r.las_prefix() +  "ipf -Pr") #print the rules
    n.r.wait_prompt()
    n.r.send(n.r.las_prefix() +  "ipf -E")
    n.r.wait_prompt()


################################################################################
#        start_apache - Start apache
################################################################################
def start_apache(n):
    # make sure the firewall is diabled
    n.r.send(n.r.las_prefix() +  "ipf -D")
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

            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.otherwebsite.com\n' +
                     'Connection: close\n',
                     sudo = False)
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


################################################################################
#        syntax - Test the IP filter rule syntax
################################################################################
class syntax:
    '''Rule syntax.

    Verify IP filter rule syntax.
    Pass/Fail criteria: It must be possible to add all example IP filter rules
                        from the manual without any errors both with the shell
                        command and from a rule file.
    '''

    def config(self):
        self.eta = 1
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # Check that the ipf command is available
        n.r.send(n.r.las_prefix() + "ipf")
        n.r.expect_exact_and_wait_prompt('firewall configuration')
        n.r.send(n.r.las_prefix() + "ipf -V")
        n.r.wait_prompt()


################################################################################
#        index - Test the IP filter rule index
################################################################################
class index:
    '''Rule index.

    Verify IP filter rule index.
    Pass/Fail criteria: It must be possible to add an IP and MAC filter rule based
                        on index in the list of rules. The rule must be placed on
                        a certain index in then list and not as the last rule.
    '''

    def config(self):
        self.eta = 2
        self.hosts = 3
        self.v6 = True
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.net_layout = 'ownlayout'

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        n.r.send(n.r.las_prefix() +  "ipf -D")
        n.r.wait_prompt()
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -m -Frls")
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -Frls")

        n.r.expect_prompt(n.r.las_prefix() +  "ipf %s pass in all" % IF(v6, '-6', ''))
        n.r.expect_prompt(n.r.las_prefix() +  "ipf %s block in all" % IF(v6, '-6', ''))
        n.r.expect_prompt(n.r.las_prefix() +  "ipf %s @2 pass in log all" % IF(v6, '-6', '')) # insert between the two previous
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -m pass in all")
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -m block in all")
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -m @2 pass in log all") # insert between the two previous
        n.r.send(n.r.las_prefix() +  "ipf -Pr")
        n.r.expect_exact("AF_INET%s: @1 pass in all" % IF(v6, '6', ''))
        n.r.expect_exact("AF_INET%s: @2 pass in log all" % IF(v6, '6', ''))
        n.r.expect_exact("AF_INET%s: @3 block in all" % IF(v6, '6', ''))
        n.r.wait_prompt()
        n.r.send(n.r.las_prefix() +  "ipf -m -Pr")
        n.r.expect_exact(["MAC:@1 pass in all", "MAC: @1 pass in all"])
        n.r.expect_exact(["MAC:@2 pass in log all", "MAC: @2 pass in log all"])
        n.r.expect_exact(["MAC:@3 block in all", "MAC: @3 block in all"])
        n.r.wait_prompt()


################################################################################
#        order - Test the IP filter rule order
################################################################################
class order:
    '''Rule order.

    Verify IP filter rule order.
    Pass/Fail criteria: The IP filter shall parse all rules and use the last
                        matching rule even though there are previous rules that
                        match and later rules that do not match.
    '''

    def config(self):
        self.eta = 10
        self.hosts = 3
        self.v6 = True
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.net_layout = 'ownlayout'

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # check that the second rule is chosen (ping will succees)
        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'all'], #match
                        ['pass', 'out', 'on', n.rifs.ifname, 'all'],  #match
                        ['pass', 'out', 'on', 'fakeifname', 'all']]]   #no match

        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)

        # check that the second rule is chosen (ping will fail)
        rulesetlist = [[['pass', 'out', 'on', n.rifs.ifname, 'all'],  #match
                        ['block', 'out', 'on', n.rifs.ifname, 'all'], #match
                        ['pass', 'out', 'on', 'fakeifname', 'all']]]   #no match

        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, succeed = False)


################################################################################
#        version - Test the IP filter protocol version
################################################################################
class version:
    '''Protocol version.

    Verify IP filter protocol version.
    Pass/Fail criteria: The IP filter must be able to filter packets based on
                        the protocol version.
    '''

    def config(self):
        self.eta = 14
        self.hosts = 3
        self.v4 = False
        self.v6 = True
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.net_layout = 'ownlayout'

    def test(self, log, hosts, v6, __):
        import util
        n = layout_net('rcs', hosts)
        pfx = 120
        ab = abnet6 + ':' + abnet
        c6 = n.cif.add_ip("%s%s.1/%s" % (ab, n.cnet, pfx))
        s6 = n.sif.add_ip("%s%s.3/%s" % (ab, n.snet, pfx))
        rc = n.rifc.add_ip("%s%s.3/%s" % (ab, n.cnet, pfx))
        rs = n.rifs.add_ip("%s%s.1/%s" % (ab, n.snet, pfx))
        n.c.add_route(s6.mask(pfx), rc)
        n.s.add_route(c6.mask(pfx), rs)

        # check that v4 traffic is blocked while v6 pass
        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'all']]] #match
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, '') #rule is for v4
            n.c.ping(s6, count = 1, retries = 2)
            n.c.ping(n.s.ip(), count = 1, retries = 2, succeed = False)

        # check that v6 traffic is blocked while v4 pass
        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'all']]] #match
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, '6') #rule is for v6
            n.c.ping(n.s.ip(), count = 1, retries = 2)
            n.c.ping(s6, count = 1, retries = 2, succeed = False)


################################################################################
#        protocol - Test the IP filter protocol number
################################################################################
class protocol:
    '''Protocol number.

    Verify IP filter protocol number.
    Pass/Fail criteria: The IP filter must be able to filter packets based on
                        the protocol number. It must be possible to configure
                        the protocol number in the rule with a string
                        or decimal number.
    '''

    def config(self):
        self.eta = 28
        self.hosts = 3
        self.v6 = True
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.net_layout = 'ownlayout'

    def test(self, log, hosts, v6, __):
        global dstport
        global srcport
        local_dstport = dstport
        local_srcport = srcport
        
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all']]]

        # first check that protocols all succeed
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)
            local_dstport += 1
            local_srcport += 1
            echo(n, local_dstport, local_srcport, 'udp', v6)
            echo(n, local_dstport, local_srcport, 'tcp', v6)
            if n.s.type != 'linux' and n.c.type != 'linux':
                echo(n, 0, 0, 'raw', v6)

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto', 'icmp', 'all'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto', 'ipv6-icmp', 'all'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto', 'udp', 'all'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto', 'tcp', 'all'],
                        ['block', 'out', 'quick', 'on', n.rifs.ifname, 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto', '1', 'all'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto', '58', 'all'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto', '17', 'all'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto', '6', 'all'],
                        ['block', 'out', 'quick', 'on', n.rifs.ifname, 'all']]]

        # check that ICMP, ICMPv6, UDP and TCP will pass but RAW will fail
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)
            local_dstport += 1
            local_srcport += 1            
            echo(n, local_dstport, local_srcport, 'udp', v6)
            echo(n, local_dstport, local_srcport, 'tcp', v6)
            if n.s.type != 'linux' and n.c.type != 'linux':
                echo(n, 0, 0, 'raw', v6, succeed = False)

################################################################################
#       ttl  - Test the IP filter ttl keyword
################################################################################
class ttl:
    '''Keyword ttl.

    Verify IP filter keyword ttl.
    Pass/Fail criteria: The IP filter must be able to filter packets based on
                        the ttl/hlim field in the IPv4/IPv6 header.
    '''

    def config(self):
        self.eta = 9
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        rulesetlist = [[['block', 'in', 'quick', 'on', n.rifc.ifname, 'ttl', '22', 'all'],
                        ['pass', 'in', 'on', n.rifc.ifname, 'all']]]

        # check that ICMP, ICMPv6 with default ttl will pass and ICMP, ICMPv6 with ttl = 22 will be blocked
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)
            n.c.ping(n.s.ip(), count = 1, retries = 2, ttl = 22, succeed = False)



################################################################################
#       tos  - Test the IP filter tos keyword
################################################################################
class tos:
    '''Keyword tos.

    Verify IP filter keyword tos.
    Pass/Fail criteria: The IP filter must be able to filter packets based on
                        the tos/tclass field in the IPv4/IPv6 header. It must
                        be possible to mask certain bits in the tos field with
                        a tos mask.
    '''

    def config(self):
        self.eta = 16
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        rulesetlist = [[['block', 'in', 'quick', 'on', n.rifc.ifname, 'tos', '0x80', 'all'],
                        ['pass', 'in', 'on', n.rifc.ifname, 'all']]]

        # check that ICMP, ICMPv6 with default ttl will pass and ICMP, ICMPv6 with tos/tclass = 128 will be blocked
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)
            n.c.ping(n.s.ip(), count = 1, retries = 2, tos = 128, succeed = False)


        rulesetlist = [[['block', 'in', 'quick', 'on', n.rifc.ifname, 'tos', '0x80/0xFE', 'all'],
                        ['pass', 'in', 'on', n.rifc.ifname, 'all']]]

        # check that ICMP, ICMPv6 with tos/tclass = 130 will pass and ICMP, ICMPv6 with tos/tclass = 128,129 will be blocked
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, tos = 130)
            n.c.ping(n.s.ip(), count = 1, retries = 2, tos = 128, succeed = False)
            n.c.ping(n.s.ip(), count = 1, retries = 2, tos = 129, succeed = False)


################################################################################
#       pktflags_tunnel  - Test the IP filter pktflags keyword
################################################################################
class pktflags_tunnel:
    '''Keyword pktflags with tunnels.

    Verify IP filter packetflags with tunnels.
    Pass/Fail criteria: The IP filter must be able to filter on packet flags
                        and detect tunneled packets.
    '''

    def config(self):
        self.eta = 39
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.rshell = n.r.ipcom_shell()

        # tunnel config
        tunnel_addrs = (n.s.alloc_ip(v6 = v6, net = 140),
                        n.r.alloc_ip(v6 = v6, net = 140))

        tunnel_ifs = (n.s.add_netif(addr = tunnel_addrs[0],
                                     tunnel = "ip",
                                     tunnel_local_ip = n.s.ip(),
                                     tunnel_remote_ip = n.r.ip()),
                      n.r.add_netif(addr = tunnel_addrs[1],
                                     tunnel = "ip",
                                     tunnel_local_ip = n.r.ip(),
                                     tunnel_remote_ip = n.s.ip()))

        # check tunnel connection before any firewall rules
        n.s.ping(tunnel_addrs[1], count = 1, retries = 2)

        rulesetlist = [[['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, \
                         'proto %s' % IF(v6, 'ipv6', 'ipip'), 'all'],
                        ['block', 'in', 'log', 'quick', 'on', tunnel_ifs[1].ifname, 'pktflags T', \
                         'proto %s' % IF(v6, 'ipv6-icmp', 'icmp'), 'all', 'icmp-type %s' % IF(v6, '128', '8')],
                        ['pass', 'in', 'log', 'on', n.rifs.ifname, \
                         'proto %s' % IF(v6, 'ipv6-icmp', 'icmp'), 'all', 'icmp-type %s' % IF(v6, '128', '8')]]]

        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

            for size in [100, 2000]:
                # check that normal ping succeeds because of rule 3
                n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                n.s.ping(n.rips.addr, count = 1, retries = 2, packetsize = size)
                n.r.send(n.r.las_prefix() + "ipf -Pl")
                n.r.expect_exact(r"0:3 p %s -> %s PR %s" % (n.s.ip().addr,
                                                            n.rips.addr,
                                                            IF(v6, 'ipv6-icmp', 'icmp')))
                n.r.wait_prompt()

                # check that tunneled ping fails because of rule 2
                n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                n.s.ping(tunnel_addrs[1], count = 1, retries = 2, packetsize = size, succeed = False)
                n.r.send(n.r.las_prefix() + "ipf -Pl")
                n.r.expect_exact(r"0:1 p %s -> %s PR %s" % (n.s.ip().addr,
                                                            n.rips.addr,
                                                            IF(v6, 'ipv6', 'ipip')))
                n.r.expect_exact(r"0:2 b %s -> %s PR %s" % (tunnel_addrs[0].addr,
                                                            tunnel_addrs[1].addr,
                                                            IF(v6, 'ipv6-icmp', 'icmp')))
                n.r.wait_prompt()


        # destroy tunnel
        for t in tunnel_ifs:
            t.destroy()



################################################################################
#       pktflags_nat  - Test the IP filter pktflags keyword
################################################################################
class pktflags_nat:
    '''Keyword pktflags with NAT.

    Verify IP filter packetflags with NAT.
    Pass/Fail criteria: The IP filter must be able to filter on packet flags
                        and detect NAT packets.
    '''

    def config(self):
        self.eta = 25
        self.hosts = 4
        self.v6 = False
        self.net_layout = 'nat'
        self.works_on_lkm = True
        self.works_on_gpp = False

    def test(self, log, n, v6, __):
        global dstport
        global srcport
        local_dstport = dstport
        local_srcport = srcport
        
        cip24 = n.c.ip().mask(24)
        rip24 = n.rips.mask(24)
        ifc = n.rifs.ifname
        nextnatport = natport
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()
        n.wshell = n.w.ipcom_shell()

        nat_ruleset = [["map", ifc, "0/0", "to", "0/32", "portmap", "tcp/udp",str(natport)+":"+str(natport+999)],
                       ["map", ifc, "0/0", "to", "0/32", "icmpidmap", "icmp",str(natport)+":"+str(natport+999)],
                       ["map", ifc, "0/0", "to", "0/32"]]

        rulesetlist = [[['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags N', 'proto icmp', 'all', 'icmp-type 0'],
                        ['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags N', 'proto udp', 'all'],
                        ['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags N', 'proto tcp', 'all'],
                        ['block', 'in', 'log', 'on', n.rifs.ifname, 'all']]]

        # this test requires s to be configured with a route back to c and w
        n.s.send_and_wait_prompt('route add -net %s %s' % (cip24, n.rips.addr))
        n.s.send_and_wait_prompt('route show -inet')

        for ruleset in rulesetlist:
            # check connection
            n.r.expect_prompt(n.r.las_prefix() + "nat -F")
            n.r.expect_prompt(n.r.las_prefix() + "nat -Z")
            n.r.expect_prompt(n.r.las_prefix() + "ipf -Fr")
            n.c.ping(n.s.ip(), count = 1, retries = 2)

            # add firewall rules
            add_ruleset(n, ruleset, v6)

            # check that ping fails because of rule 4
            n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
            n.c.ping(n.s.ip(), count = 1, retries = 2, succeed = False)
            n.r.send(n.r.las_prefix() + "ipf -Pl")
            n.r.expect_exact(r"0:4 b %s -> %s PR %s" % (n.s.ip().addr,
                                                        n.c.ip().addr,
                                                        'icmp'))
            n.r.wait_prompt()

            # add NAT rules
            n.r.expect_prompt(n.r.las_prefix() + "nat -F")
            n.r.expect_prompt(n.r.las_prefix() + "nat -Z")
            for rule in nat_ruleset:
                rule = n.r.las_prefix() + "nat " + " ".join(rule)
                n.r.expect_prompt(rule)
            n.r.send(n.r.las_prefix() + "nat -l")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() + "nat -E")
            n.r.wait_prompt()

            # check that ping succeeds because of rule 1
            for size in [100, 2000]:
                # ICMP
                n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                n.c.ping(n.s.ip(), count = 1, retries = 2, packetsize = size)
                n.r.send(n.r.las_prefix() + "ipf -Pl")
                n.r.expect_exact(r"0:1 p %s -> %s PR %s" % (n.s.ip().addr,
                                                            n.c.ip().addr,
                                                            'icmp'))
                n.r.wait_prompt()
                n.r.send(n.r.las_prefix() + "nat -m")
                n.r.expect_exact("NAT MAPPINGS TABLE:")
                n.r.expect_re(r"%s:[0-9]+ -> %s:0 proto icmp, \(%s:[0-9]+\)" % (n.c.ip().addr,
                                                                                n.s.ip().addr,
                                                                                n.rips.addr))
                n.r.wait_prompt()
                n.r.expect_prompt(n.r.las_prefix() + "nat -C")

                # UDP
                n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                local_dstport += 1    # avoid S_errno_EADDRINUSE error
                local_srcport += 1    # avoid S_errno_EADDRINUSE error
                echo(n, local_dstport, local_srcport, 'udp', v6, chunk_size = size)
                n.r.send(n.r.las_prefix() + "ipf -Pl")
                n.r.expect_exact(r"0:2 p %s,%d -> %s,%d PR %s" % (n.s.ip().addr, local_dstport,
                                                                  n.c.ip().addr, local_srcport,
                                                                  'udp'))
                n.r.wait_prompt()
                n.r.send(n.r.las_prefix() + "nat -m")
                n.r.expect_exact("NAT MAPPINGS TABLE:")
                n.r.expect_exact(r"%s:%s -> %s:%s proto %s, (%s:%s)" % (n.c.ip().addr,
                                                                        local_srcport,
                                                                        n.s.ip().addr,
                                                                        local_dstport,
                                                                        'udp',
                                                                        n.rips.addr,
                                                                        str(nextnatport)))
                nextnatport = nextnatport + 1
                n.r.wait_prompt()
                n.r.expect_prompt(n.r.las_prefix() + "nat -C")

                # TCP
                n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                echo(n, local_dstport, local_srcport, 'tcp', v6, chunk_size = size)
                n.r.send(n.r.las_prefix() + "ipf -Pl")
                n.r.expect_exact(r"0:3 p %s,%d -> %s,%d PR %s" % (n.s.ip().addr, local_dstport,
                                                                  n.c.ip().addr, local_srcport,
                                                                  'tcp'))
                n.r.wait_prompt()
                n.r.send(n.r.las_prefix() + "nat -m")
                n.r.expect_exact("NAT MAPPINGS TABLE:")
                n.r.expect_exact(r"%s:%s -> %s:%s proto %s, (%s:%s)" % (n.c.ip().addr,
                                                                        local_srcport,
                                                                        n.s.ip().addr,
                                                                        local_dstport,
                                                                        'tcp',
                                                                        n.rips.addr,
                                                                        str(nextnatport)))
                nextnatport = nextnatport + 1
                n.r.wait_prompt()
                n.r.expect_prompt(n.r.las_prefix() + "nat -C")

            n.r.send(n.r.las_prefix() + "nat -D")
            n.r.wait_prompt()
            n.r.expect_prompt(n.r.las_prefix() + "nat -F")
            n.r.expect_prompt(n.r.las_prefix() + "nat -Z")


        # remove the route
        n.s.send_and_wait_prompt('route delete -net %s %s' % (cip24, n.rips.addr))
        n.s.send_and_wait_prompt('route show -inet')

################################################################################
#       ipsecstate  - Test the ipsec state with ipsec tunnel
################################################################################
class ipsecstate:
    '''Keyword ipsec state with IPSEC tunnel.

    Verify that the ipsec state works.
    Pass/Fail criteria: The firewall shall set up a ipsec state and let
                        ipsec traffic pass. When changing the tunnel
                        gateway address the traffic will be blocked.
    '''

    def config(self):
        self.eta = 15 
        self.hosts = 4 
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('ipsec' + v6, hosts)

        # create shells
        n.sshell = n.s.ipcom_shell()
        n.r1shell = n.r1.ipcom_shell()
        n.r2shell = n.r2.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        # ipsec configuration
        if v6:
            mask = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        else:
            mask = '255.255.255.255'
        ipsec_commands = ['keyadm flush',
                          # output
                          'keyadm add -new -proto protocolspec ealgspec aalgspec -spi 603 -dst %s -src %s %s %s \
                          tunnelspec -replay 0' % ('sa_dst', 'sa_src', 'ekeyspec', 'akeyspec'),
                          'keyadm addflow -spi 603 -dst %s -proto protocolspec -srcmask %s -dstmask %s -srcflow %s \
                          -dstflow %s' % ('sa_dst', mask, mask, 'srcip', 'dstip'),
                          # input
                          'keyadm add -new -proto protocolspec ealgspec aalgspec -spi 603 -dst %s -src %s %s %s \
                          -ingress -replay 0' % ('sa_src', 'sa_dst', 'ekeyspec', 'akeyspec'),
                          'keyadm addflow -spi 603 -dst %s -proto protocolspec -srcmask %s -dstmask %s -srcflow %s \
                          -dstflow %s -ingress' % ('sa_src', mask, mask, 'dstip', 'srcip'),
                          'keyadm dump']

        # ah and esp mode
        for protocol in ['ah', 'esp']:
            if protocol == 'ah':
                ealg = ''
                aalg = '-auth sha1'
                ekey = ''
                akey = '-akey 8317954752bf255b5321fe19e54a7f8d83179547'
            else:
                ealg = '-enc 3des'
                aalg = '-auth sha1'
                ekey = '-ekey b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480'
                akey = '-akey 8317954752bf255b5321fe19e54a7f8d83179547'

            # check connection before any ipsec or firewall rules
            n.r1.send(n.r1.las_prefix() +  "keyadm flush")
            n.r1.wait_prompt()
            n.r2.send(n.r2.las_prefix() +  "keyadm flush")
            n.r2.wait_prompt()

            n.r2.expect_prompt(n.r2.las_prefix() + "ipf -Fr")
            n.s.ping(n.r2_ips.addr, count = 1, retries = 2)
            n.c.ping(n.r1_ipc.addr, count = 1, retries = 2)

            rulesetlist = [[['block', 'in' ,'log', 'on', n.r1_ifs.ifname, 'all'],
                            ['pass', 'out', 'log' , 'on', n.r1_ifs.ifname, 'proto', 'udp', 'from', 'any', \
                            'to', 'any', 'keep', 'ipsecstate'],
                            ['pass', 'out', 'quick', 'on', n.r1_ifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #allow ND
                            ['pass', 'out', 'quick', 'on', n.r1_ifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #allow ND
                            ['pass', 'in', 'quick', 'on', n.r1_ifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #allow ND
                            ['pass', 'in', 'quick', 'on', n.r1_ifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136']]] #allow ND

            for ruleset in rulesetlist:
                n.r1.send(n.r1.las_prefix() +  "ipf -D")
                n.r1.wait_prompt()
                n.r1.expect_prompt(n.r1.las_prefix() +  "ipf -m -Frls")
                n.r1.expect_prompt(n.r1.las_prefix() +  "ipf -Frls")
                n.r1.expect_prompt(n.r1.las_prefix() +  "ipf -Z")

                for rule in ruleset:
                    if v6:
                        rule = "ipf -6 " + " ".join(rule)
                    else:
                        rule = "ipf " + " ".join(rule)
                    n.r1.expect_prompt(n.r1.las_prefix() + rule)

                n.r1.send(n.r1.las_prefix() +  "ipf -Pr") #print the rules
                n.r1.wait_prompt()
                n.r1.send(n.r1.las_prefix() +  "ipf -E")
                n.r1.wait_prompt()

                # configure ipsec
                for cmd in ipsec_commands:
                    cmd = cmd.replace('dstip', n.c.ip().addr)
                    cmd = cmd.replace('srcip', n.s.ip().addr)
                    cmd = cmd.replace('sa_src', n.r2_ipc.addr)
                    cmd = cmd.replace('sa_dst', n.r1_ips.addr)
                    cmd = cmd.replace('tunnelspec', '-forcetunnel')
                    cmd = cmd.replace('protocolspec', protocol)
                    cmd = cmd.replace('ealgspec', ealg)
                    cmd = cmd.replace('aalgspec', aalg)
                    cmd = cmd.replace('ekeyspec', ekey)
                    cmd = cmd.replace('akeyspec', akey)
                    n.r2.send(n.r2.las_prefix() + cmd)
                    n.r2.expect_exact('err=0')
                    n.r2.wait_prompt()

                for cmd in ipsec_commands:
                    cmd = cmd.replace('dstip', n.s.ip().addr)
                    cmd = cmd.replace('srcip', n.c.ip().addr)
                    cmd = cmd.replace('sa_src', n.r1_ips.addr)
                    cmd = cmd.replace('sa_dst', n.r2_ipc.addr)
                    cmd = cmd.replace('tunnelspec', '-forcetunnel')
                    cmd = cmd.replace('protocolspec', protocol)
                    cmd = cmd.replace('ealgspec', ealg)
                    cmd = cmd.replace('aalgspec', aalg)
                    cmd = cmd.replace('ekeyspec', ekey)
                    cmd = cmd.replace('akeyspec', akey)
                    n.r1.send(n.r1.las_prefix() + cmd)
                    n.r1.expect_exact('err=0')
                    n.r1.wait_prompt()

                # Send and receive packet
                s_port = 45001
                c_port = 45002
                n.s.send(n.s.las_prefix() + "socktest open -d inet%s -t dgram -p udp" % v6)
                s_sock = n.s.expect_get("Socket = ([0-9]+)\s")
                n.s.send(n.s.las_prefix() + "socktest bind -s %s -p %s" % (s_sock, s_port))
                n.s.wait_prompt()
                n.c.send(n.c.las_prefix() + "socktest open -d inet%s -t dgram -p udp" % v6)
                c_sock = n.c.expect_get("Socket = ([0-9]+)\s")
                n.c.send(n.c.las_prefix() + "socktest bind -s %s -p %s" % (c_sock, c_port))
                n.c.wait_prompt()
                n.c.send(n.c.las_prefix() + "socktest send -s %s -d xxx -a %s -p %s" % (c_sock, n.s.ip().addr, s_port))
                n.c.wait_prompt()

                # Check log for state
                n.r1.send(n.r1.las_prefix() + "ipf -P s")
                n.r1.expect_re(r"%s:%s -> %s:%s proto udp" % (n.c.ip().addr, c_port, n.s.ip().addr, s_port))
                n.r1.wait_prompt()

                # Make sure the state works
                n.s.send(n.s.las_prefix() + "socktest send -s %s -d yyy -a %s -p %s" % (s_sock, n.c.ip().addr, c_port))
                n.s.wait_prompt()
                n.r1.send(n.r1.las_prefix() + "ipf -P l")
                n.r1.expect_re(r"p %s,[0-9]+ -> %s,[0-9]+ PR udp" % (n.c.ip().addr, n.s.ip().addr))
                n.r1.wait_prompt()

                # Clear log and take down the ipsec tunnel
                n.r1.expect_prompt(n.r1.las_prefix() +  "ipf -F l")
                n.r1.send(n.r1.las_prefix() +  "keyadm flush")
                n.r1.wait_prompt()
                n.r2.send(n.r2.las_prefix() +  "keyadm flush")
                n.r2.wait_prompt()

                # Calculate a new ip-address
                ab = IF(v6, abnet6 + ':', abnet)
                if v6:
                    nodad = "nodad"
                    r2_addr = abnet.split('.')
                    r_temp = ab + str(hex(int(r2_addr[0]))[2:]) + "%02X" % (int(r2_addr[1]),)  + ":" + str(int(n.r2_ipc.addr[-3:])+1)
                else:
                    nodad = ""
                    r2_addr = n.r2_ipc.addr.split('.')
                    r_temp = r2_addr[0] + '.' + r2_addr[1] + '.' + r2_addr[2] + '.' + str(int(r2_addr[3]) + 1)
                
                # Add new vlan
                n.r2.expect_prompt(n.r2.las_prefix() +  "ifconfig %s down" % n.r2_ifc.ifname)
                n.r2.expect_prompt(n.r2.las_prefix() +  "ifconfig %s destroy" % n.r2_ifc.ifname)
                n.r2.expect_prompt(n.r2.las_prefix() +  "ifconfig %s create" % n.r2_ifc.ifname)
                n.r2.expect_prompt(n.r2.las_prefix() +  "ifconfig %s vlan %s vlanif eth0" % \
                                                        (n.r2_ifc.ifname,str(n.r2_ifc.ifname)[4:])) 
                n.r2.expect_prompt(n.r2.las_prefix() +  "ifconfig %s mtu 1200" % n.r2_ifc.ifname)
                n.r2.expect_prompt(n.r2.las_prefix() +  "ifconfig %s up" % n.r2_ifc.ifname)
                n.r2.expect_prompt(n.r2.las_prefix() +  "ifconfig %s inet%s add %s %s" % (n.r2_ifc.ifname, v6, \
                                                        str(r_temp)+"/" + str(IF(v6, 120, 24)), nodad))

                # configure ipsec
                for cmd in ipsec_commands:
                    cmd = cmd.replace('dstip', n.c.ip().addr)
                    cmd = cmd.replace('srcip', n.s.ip().addr)
                    cmd = cmd.replace('sa_src', r_temp)
                    cmd = cmd.replace('sa_dst', n.r1_ips.addr)
                    cmd = cmd.replace('tunnelspec', '-forcetunnel')
                    cmd = cmd.replace('protocolspec', protocol)
                    cmd = cmd.replace('ealgspec', ealg)
                    cmd = cmd.replace('aalgspec', aalg)
                    cmd = cmd.replace('ekeyspec', ekey)
                    cmd = cmd.replace('akeyspec', akey)
                    n.r2.send(n.r2.las_prefix() + cmd)
                    n.r2.expect_exact('err=0')
                    n.r2.wait_prompt()

                for cmd in ipsec_commands:
                    cmd = cmd.replace('dstip', n.s.ip().addr)
                    cmd = cmd.replace('srcip', n.c.ip().addr)
                    cmd = cmd.replace('sa_src', n.r1_ips.addr)
                    cmd = cmd.replace('sa_dst', r_temp)
                    cmd = cmd.replace('tunnelspec', '-forcetunnel')
                    cmd = cmd.replace('protocolspec', protocol)
                    cmd = cmd.replace('ealgspec', ealg)
                    cmd = cmd.replace('aalgspec', aalg)
                    cmd = cmd.replace('ekeyspec', ekey)
                    cmd = cmd.replace('akeyspec', akey)
                    n.r1.send(n.r1.las_prefix() + cmd)
                    n.r1.expect_exact('err=0')
                    n.r1.wait_prompt()

                # Send packet from server to client
                # Check if packet is blocked due to new ipsec tunnel address
                n.s.send(n.s.las_prefix() + "socktest send -s %s -d yyy -a %s -p %s" % (s_sock, n.c.ip().addr, c_port))
                n.s.wait_prompt()
                n.r1.send(n.r1.las_prefix() + "ipf -P l")
                n.r1.expect_re(r"b %s,[0-9]+ -> %s,[0-9]+ PR udp" % (n.s.ip().addr, n.c.ip().addr))
                n.r1.wait_prompt()

                # Send packet from client to server
                # Clear log and set up a new state
                n.c.send(n.c.las_prefix() + "socktest send -s %s -d xxx -a %s -p %s" % (c_sock, n.s.ip().addr, s_port))
                n.c.wait_prompt()

                # Send packet from server to client
                # Check if packet is passed in firewall
                n.s.send(n.s.las_prefix() + "socktest send -s %s -d yyy -a %s -p %s" % (s_sock, n.c.ip().addr, c_port))
                n.s.wait_prompt()
                n.r1.send(n.r1.las_prefix() + "ipf -P l")
                n.r1.expect_re(r"p %s,[0-9]+ -> %s,[0-9]+ PR udp" % (n.c.ip().addr, n.s.ip().addr))
                n.r1.wait_prompt()

                # Close open sockets
                n.c.send(n.c.las_prefix() + "socktest close -s %s" % c_sock)
                n.c.wait_prompt()
                n.s.send(n.c.las_prefix() + "socktest close -s %s" % s_sock)
                n.s.wait_prompt()


################################################################################
#       pktflags_ipsec  - Test the IP filter pktflags keyword
################################################################################
class pktflags_ipsec:
    '''Keyword pktflags with IPSEC.

    Verify IP filter packetflags with IPSEC.
    Pass/Fail criteria: The IP filter must be able to filter on packet flags
                        and detect IPSEC packets in tunnel/transport mode.
                        for both AH and ESP
    '''

    def config(self):
        self.eta = 39
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        global dstport
        global srcport
        local_dstport = dstport
        local_srcport = srcport
        
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.rshell = n.r.ipcom_shell()

        # ipsec configuration
        if v6:
            mask = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        else:
            mask = '255.255.255.255'
        ipsec_commands = ['keyadm flush',
                          # output
                          'keyadm add -new -proto protocolspec ealgspec aalgspec -spi 603 -dst %s -src %s %s %s tunnelspec -replay 0' \
                          % ('dstip', 'srcip', 'ekeyspec', 'akeyspec'),
                          'keyadm addflow -spi 603 -dst %s -proto protocolspec -srcmask %s -dstmask %s -srcflow %s -dstflow %s' \
                          % ('dstip', mask, mask, 'srcip', 'dstip'),
                          # input
                          'keyadm add -new -proto protocolspec ealgspec aalgspec -spi 603 -dst %s -src %s %s %s -ingress -replay 0' \
                          % ('srcip', 'dstip', 'ekeyspec', 'akeyspec'),
                          'keyadm addflow -spi 603 -dst %s -proto protocolspec -srcmask %s -dstmask %s -srcflow %s -dstflow %s -ingress' \
                          % ('srcip', mask, mask, 'dstip', 'srcip'),
                          'keyadm dump']

        # ah and esp mode
        for protocol in ['ah', 'esp']:
            if protocol == 'ah':
                ealg = ''
                aalg = '-auth sha1'
                ekey = ''
                akey = '-akey 8317954752bf255b5321fe19e54a7f8d83179547'
            else:
                ealg = '-enc 3des'
                aalg = '-auth sha1'
                ekey = '-ekey b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480'
                akey = '-akey 8317954752bf255b5321fe19e54a7f8d83179547'

            # transport and tunnel mode
            for mode in ['', '-forcetunnel']:
                # check connection before any ipsec or firewall rules
                n.r.send(n.r.las_prefix() +  "keyadm flush")
                n.r.wait_prompt()
                n.s.send(n.s.las_prefix() +  "keyadm flush")
                n.s.wait_prompt()
                n.c.send(n.c.las_prefix() +  "keyadm flush")
                n.c.wait_prompt()
                n.r.expect_prompt(n.r.las_prefix() + "ipf -Fr")
                n.s.ping(n.rips.addr, count = 1, retries = 2)

                rulesetlist = [[['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags S', \
                                 'proto %s' % IF(v6, 'ipv6-icmp', 'icmp'), 'all', 'icmp-type %s' % IF(v6, '128', '8')], #transport mode
                                ['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags ST', \
                                 'proto %s' % IF(v6, 'ipv6-icmp', 'icmp'), 'all', 'icmp-type %s' % IF(v6, '128', '8')], #tunnel mode
                                ['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags S', 'proto udp', 'all'],  #transport mode
                                ['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags ST', 'proto udp', 'all'], #tunnel mode
                                ['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags S', 'proto tcp', 'all'],  #transport mode
                                ['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'pktflags ST', 'proto tcp', 'all'], #tunnel mode
                                ['block', 'in', 'log', 'on', n.rifs.ifname, \
                                 'proto %s' % IF(v6, 'ipv6-icmp', 'icmp'), 'all', 'icmp-type %s' % IF(v6, '128', '8')]]]

                for ruleset in rulesetlist:
                    add_ruleset(n, ruleset, v6)
                    # check that ping fails because of rule 7
                    n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                    n.s.ping(n.rips.addr, count = 1, retries = 2, succeed = False)
                    n.r.send(n.r.las_prefix() + "ipf -Pl")
                    n.r.expect_exact(r"0:7 b %s -> %s PR %s" % (n.s.ip().addr,
                                                                n.rips.addr,
                                                                IF(v6, 'ipv6-icmp', 'icmp')))
                    n.r.wait_prompt()
                    # configure ipsec
                    for cmd in ipsec_commands:
                        cmd = cmd.replace('dstip', n.rips.addr)
                        cmd = cmd.replace('srcip', n.s.ip().addr)
                        cmd = cmd.replace('tunnelspec', mode)
                        cmd = cmd.replace('protocolspec', protocol)
                        cmd = cmd.replace('ealgspec', ealg)
                        cmd = cmd.replace('aalgspec', aalg)
                        cmd = cmd.replace('ekeyspec', ekey)
                        cmd = cmd.replace('akeyspec', akey)
                        n.s.send(n.s.las_prefix() + cmd)
                        n.s.expect_exact('err=0')
                        n.s.wait_prompt()

                    for cmd in ipsec_commands:
                        cmd = cmd.replace('dstip', n.s.ip().addr)
                        cmd = cmd.replace('srcip', n.rips.addr)
                        cmd = cmd.replace('tunnelspec', mode)
                        cmd = cmd.replace('protocolspec', protocol)
                        cmd = cmd.replace('ealgspec', ealg)
                        cmd = cmd.replace('aalgspec', aalg)
                        cmd = cmd.replace('ekeyspec', ekey)
                        cmd = cmd.replace('akeyspec', akey)
                        n.r.send(n.r.las_prefix() + cmd)
                        n.r.expect_exact('err=0')
                        n.r.wait_prompt()

                    # check that ping succeeds because of rule 1 (transport mode) or 2 (tunnel mode)
                    for size in [100, 2000]:
                        # ICMP
                        n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                        n.s.ping(n.rips.addr, count = 1, retries = 2, packetsize = size)
                        n.r.send(n.r.las_prefix() + "ipf -Pl")
                        n.r.expect_exact(r"0:%s p %s -> %s PR %s" % (IF(mode == '-forcetunnel', '2', '1'),
                                                                     n.s.ip().addr,
                                                                     n.rips.addr,
                                                                     IF(v6, 'ipv6-icmp', 'icmp')))
                        n.r.wait_prompt()
                        # UDP
#                         n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
#                         echo_ipsec(n, dstport, srcport, 'udp', v6, chunk_size = size)
#                         n.r.send(n.r.las_prefix() + "ipf -Pl")
#                         n.r.expect_exact(r"0:%s p %s,%d -> %s,%d PR udp" % (IF(mode == '-forcetunnel', '4', '3'),
#                                                                             n.s.ip().addr, srcport,
#                                                                             n.rips.addr, dstport))
#                         n.r.wait_prompt()
                        # TCP
                        n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                        local_dstport += 1
                        local_srcport += 1
                        echo_ipsec(n, local_dstport, local_srcport, 'tcp', v6, chunk_size = size)
                        n.r.send(n.r.las_prefix() + "ipf -Pl")
                        n.r.expect_exact(r"0:%s p %s,%d -> %s,%d PR tcp" % (IF(mode == '-forcetunnel', '6', '5'),
                                                                     n.s.ip().addr, local_srcport,
                                                                     n.rips.addr, local_dstport))
                        n.r.wait_prompt()




################################################################################
#       proto_ipsec  - Test the IP filter proto keyword
################################################################################
class proto_ipsec:
    '''Keyword pktflags with IPSEC.

    Verify IP filter proto keyworks for ESP and AH.
    Pass/Fail criteria: The IP filter must be able to filter on protocol type ESP and AH
    '''

    def config(self):
        self.eta = 21
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # ipsec configuration
        if v6:
            mask = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        else:
            mask = '255.255.255.255'
        ipsec_commands = ['keyadm flush',
                          # output
                          'keyadm add -new -proto protocolspec ealgspec aalgspec -spi 603 -dst %s -src %s %s %s tunnelspec' \
                          % ('dstip', 'srcip', 'ekeyspec', 'akeyspec'),
                          'keyadm addflow -spi 603 -dst %s -proto protocolspec -srcmask %s -dstmask %s -srcflow %s -dstflow %s' \
                          % ('dstip', mask, mask, 'srcip', 'dstip'),
                          # input
                          'keyadm add -new -proto protocolspec ealgspec aalgspec -spi 603 -dst %s -src %s %s %s -ingress' \
                          % ('srcip', 'dstip', 'ekeyspec', 'akeyspec'),
                          'keyadm addflow -spi 603 -dst %s -proto protocolspec -srcmask %s -dstmask %s -srcflow %s -dstflow %s -ingress' \
                          % ('srcip', mask, mask, 'dstip', 'srcip'),
                          'keyadm dump']

        # ah and esp mode
        for protocol in ['ah', 'esp']:
            if protocol == 'ah':
                ealg = ''
                aalg = '-auth sha1'
                ekey = ''
                akey = '-akey 8317954752bf255b5321fe19e54a7f8d83179547'
            else:
                ealg = '-enc 3des'
                aalg = '-auth sha1'
                ekey = '-ekey b0e39876daf6d4ee5aaa895a4733bd8afdead83a2a8aa480'
                akey = '-akey 8317954752bf255b5321fe19e54a7f8d83179547'

            # transport and tunnel mode
            for mode in ['', '-forcetunnel']:
                # check connection before any ipsec or firewall rules
                n.r.send(n.r.las_prefix() +  "keyadm flush")
                n.r.wait_prompt()
                n.s.send(n.s.las_prefix() +  "keyadm flush")
                n.s.wait_prompt()
                n.c.send(n.c.las_prefix() +  "keyadm flush")
                n.c.wait_prompt()
                n.r.expect_prompt(n.r.las_prefix() + "ipf -Fr")
                n.c.ping(n.s.ip(), count = 1, retries = 2)

                rulesetlist = [[['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'proto ah', 'all'],
                                ['pass', 'in', 'log', 'quick', 'on', n.rifs.ifname, 'proto esp', 'all'],
                                ['block', 'in', 'log', 'on', n.rifs.ifname, \
                                 'proto %s' % IF(v6, 'ipv6-icmp', 'icmp'), 'all', 'icmp-type %s' % IF(v6, '129', '0')]]]

                for ruleset in rulesetlist:
                    add_ruleset(n, ruleset, v6)
                    # check that ping fails because of rule 3
                    n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                    n.c.ping(n.s.ip(), count = 1, retries = 2, succeed = False)
                    n.r.send(n.r.las_prefix() + "ipf -Pl")
                    n.r.expect_exact(r"0:3 b %s -> %s PR %s" % (n.s.ip().addr,
                                                                n.c.ip().addr,
                                                                IF(v6, 'ipv6-icmp', 'icmp')))
                    n.r.wait_prompt()

                    # configure ipsec
                    for cmd in ipsec_commands:
                        cmd = cmd.replace('dstip', n.c.ip().addr)
                        cmd = cmd.replace('srcip', n.s.ip().addr)
                        cmd = cmd.replace('tunnelspec', mode)
                        cmd = cmd.replace('protocolspec', protocol)
                        cmd = cmd.replace('ealgspec', ealg)
                        cmd = cmd.replace('aalgspec', aalg)
                        cmd = cmd.replace('ekeyspec', ekey)
                        cmd = cmd.replace('akeyspec', akey)
                        n.s.send(n.s.las_prefix() + cmd)
                        n.s.expect_exact('err=0')
                        n.s.wait_prompt()

                    for cmd in ipsec_commands:
                        cmd = cmd.replace('dstip', n.s.ip().addr)
                        cmd = cmd.replace('srcip', n.c.ip().addr)
                        cmd = cmd.replace('tunnelspec', mode)
                        cmd = cmd.replace('protocolspec', protocol)
                        cmd = cmd.replace('ealgspec', ealg)
                        cmd = cmd.replace('aalgspec', aalg)
                        cmd = cmd.replace('ekeyspec', ekey)
                        cmd = cmd.replace('akeyspec', akey)
                        n.c.send(n.c.las_prefix() + cmd)
                        n.c.expect_exact('err=0')
                        n.c.wait_prompt()

                    # check that ping succeeds because of rule 1 (transport mode) or 2 (tunnel mode)
                    for size in [100, 2000]:
                        # ICMP
                        n.r.expect_prompt(n.r.las_prefix() + "ipf -Fl")
                        n.c.ping(n.s.ip(), count = 1, retries = 2, packetsize = size)
                        n.r.send(n.r.las_prefix() + "ipf -Pl")
                        n.r.expect_exact(r"0:%s p %s -> %s PR %s" % (IF(protocol == 'ah', '1', '2'),
                                                                     n.s.ip().addr,
                                                                     n.c.ip().addr,
                                                                     IF(protocol == 'ah', 'ah', 'esp')))
                        n.r.wait_prompt()


################################################################################
#       tcpflags  - Test the IP filter flags keyword
################################################################################
class tcpflags:
    '''Keyword flags.

    Verify IP filter TCP flags.
    Pass/Fail criteria: The IP filter must be able to filter on TCP flags in TCP
                        packets. It must be possible to filter TCP flags
                        with a mask.

    '''

    def config(self):
        self.eta = 7
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all', 'flags S'],       # SYN ->
                        ['pass', 'in', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all', 'flags SA/SAPRF'], # SYN,ACK <-
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all', 'flags A'],       # ACK ->
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all', 'flags PA/SAPRF'],# PUSH,ACK ->
                        ['pass', 'in', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all', 'flags A'],        # ACK <-
                        ['pass', 'in', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all', 'flags PA/SAPRF'], # PUSH, ACK <-
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all', 'flags FA/SAPRF'],# FIN,ACK ->
                        ['pass', 'in', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all', 'flags FA/SAPRF'], # FIN,ACK <-
                        ['block', 'in', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all'],
                        ['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'all']]]

        # Block all TCP flag combinations except the exptected
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            echo(n, dstport, srcport, 'tcp', v6)



################################################################################
#       frag  - Test the IP filter frag keyword
################################################################################
class frag:
    '''Keyword frag.

    Verify IP filter keyword frag.
    Pass/Fail criteria: The IP filter must be able to filter on fragments both
                        for IPv4 and IPv6. It must be possible to filter packet
                        with and without fragments.

    '''

    def config(self):
        self.eta = 14
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # some vxworks BSPs seem to need this (integrator1136jfs)
        check_mtu(n)

        if v6:
            rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128', 'with frag']]]
        else:
            rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'with frag']]]

        # Block all fragmented ICMP echos
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, packetsize = 1000)
            n.c.ping(n.s.ip(), count = 1, retries = 2, packetsize = 2000, succeed = False)

        if v6:
            rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128', 'with no frag']]]
        else:
            rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'with no frag']]]

        # Block all non-fragmented ICMP echos
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, packetsize = 2000)
            n.c.ping(n.s.ip(), count = 1, retries = 2, packetsize = 1000, succeed = False)


################################################################################
#       ipopts  - Test the IP filter ipopts keyword
################################################################################
class ipopts:
    '''Keyword ipopts.

    Verify IP filter keyword ipopts.
    Pass/Fail criteria: The IP filter must be able to filter on IP options. It
                        must be possible to filter packets with and without
                        IP options.
    '''

    def config(self):
        self.eta = 14
        self.hosts = 3
        self.v6 = False
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'with ipopts']]]

        # Block all ICMP echos with IP options
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)
            n.c.ping(n.s.ip(), count = 1, retries = 2, timestamp = 'tsandaddr', succeed = False)

        rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'with no ipopts']]]

        # Block all non-fragmented ICMP echos
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, timestamp = 'tsandaddr')
            n.c.ping(n.s.ip(), count = 1, retries = 2, succeed = False)


################################################################################
#       icmp_type  - Test the IP filter icmp_type keyword
################################################################################
class icmp_type:
    '''Keyword icmp_type.

    Verify IP filter keyword icmp_type.
    Pass/Fail criteria: The IP filter must be able to filter packets based on
                        the icmp type field in the ICMPv4/ICMPv6 header.
    '''

    def config(self):
        self.eta = 8
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        if v6:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #allow ND
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #allow ND
                            ['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8'],
                            ['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all']]]

        # Block all ICMP but ICMP echos
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)


################################################################################
#        log - Test IP filter logging
################################################################################
class log:
    '''Logging.

    Verify IP filter logging.
    Pass/Fail criteria: The IP filter must be able to log matching frames. The
                        "log first" keyword must limit logging to one entry
                        per rule. The maximum number of log entries must be
                        equal to 100.
    '''

    def config(self):
        self.eta = 18
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        # some vxworks BSPs seem to need this (integrator1136jfs)
        check_mtu(n)

        if v6:
            rulesetlist = [[['pass', 'out', 'log', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128']]]
        else:
            rulesetlist = [[['pass', 'out', 'log', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8']]]

        # LOG all ICMP echos
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 5, at_least = 2)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Pl")
            n.r.expect_exact(r"%s -> %s PR %s" % (n.c.ip().addr,
                                                  n.s.ip().addr,
                                                  IF(v6, 'ipv6-icmp', 'icmp')))
            n.r.expect_exact(r"%s -> %s PR %s" % (n.c.ip().addr,
                                                  n.s.ip().addr,
                                                  IF(v6, 'ipv6-icmp', 'icmp')))
            n.r.expect_exact(r"%s -> %s PR %s" % (n.c.ip().addr,
                                                  n.s.ip().addr,
                                                  IF(v6, 'ipv6-icmp', 'icmp')))
            n.r.wait_prompt()



        if v6:
            rulesetlist = [[['pass', 'out', 'log first', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128']]]
        else:
            rulesetlist = [[['pass', 'out', 'log first', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8']]]

        # LOG the first ICMP echo
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6) # will clear statistics
            n.c.ping(n.s.ip(), count = 5, at_least = 2)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("logged output packets:     blocked 0 passed 1")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Pl")
            n.r.wait_prompt()


        if v6:
            rulesetlist = [[['pass', 'out', 'log', 'quick', 'on', n.rifs.ifname, 'proto udp', 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'log', 'quick', 'on', n.rifs.ifname, 'proto udp', 'all']]]

        # Send 105 UDP packets and LOG 100
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6) # will clear statistics
            echo(n, dstport, srcport, 'udp', v6, count = 105)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("logged output packets:     blocked 0 passed 100")
            n.r.wait_prompt()


################################################################################
#        ports - Test IP filter source and destination port rules
################################################################################
class ports:
    '''Ports.

    Verify IP filter port rules.
    Pass/Fail criteria: The IP filter must be able to filter on source and
                        destination ports in UDP/TCP packets. It must be
                        possible to filter on port ranges using all port
                        range operators. It must be possible to invert a
                        port.
    '''

    def config(self):
        self.eta = 22
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        global dstport
        global srcport
        local_dstport = dstport
        local_srcport = srcport
        
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port', 'eq', str(local_dstport)], # =
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port', 'ge', str(local_dstport)], # >=
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port', 'gt', str(local_dstport-1)], # >
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port', 'le', str(local_dstport+1)], # <=
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port', 'lt', str(local_dstport+1)], # <
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port', 'ne', str(local_dstport+1)], # !=
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port',str(local_dstport+1),'or', str(local_dstport+2)], # <>
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port',str(local_dstport-1),'ir', str(local_dstport+1)],
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]

        # Check destination ports
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            echo(n, local_dstport, local_srcport, 'udp', v6)

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port', 'eq', str(local_srcport), 'to any'], # =
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port', 'ge', str(local_srcport), 'to any'], # >=
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port', 'gt', str(local_srcport-1), 'to any',], # >
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port', 'le', str(local_srcport+1), 'to any'], # <=
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port', 'lt', str(local_srcport+1), 'to any'], # <
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port', 'ne', str(local_srcport+1), 'to any'], # !=
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port',str(local_srcport+1),'or', str(local_srcport+2), 'to any'], # <>
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']],
                       [['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port',str(local_srcport-1),'ir', str(local_srcport+1), 'to any'], # ><
                        ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]

        # Check source ports
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            echo(n, local_dstport, local_srcport, 'udp', v6)

################################################################################
#        udp_frag_port - Test IP filter destination port rules on frag packets
################################################################################
class udp_frag_port:
    '''udp_frag_port.

    Verify IP filter port rules.
    Pass/Fail criteria: The IP filter must be able to filter on 
                        destination ports in UDP packets. 
                        If the port is correct, match the rule;
                        otherwise, do not filter(pass).
    '''

    def config(self):
        self.eta = 22
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        global dstport
        global srcport
        local_dstport = dstport
        local_srcport = srcport
        
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'to any', 'port', 'eq', str(local_dstport)]]] # =

        # Check destination ports
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            echo(n, local_dstport, local_srcport, 'udp', v6, succeed = False, chunk_size = 4096)
            echo(n, local_dstport+1, local_srcport, 'udp', v6, succeed = True, chunk_size = 4096)

        rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any', 'port', 'eq', str(local_srcport), 'to any']]] # =

        # Check source ports
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            echo(n, local_dstport, local_srcport, 'udp', v6, succeed = False, chunk_size = 4096)
            echo(n, local_dstport, local_srcport+1, 'udp', v6, succeed = True, chunk_size = 4096)


################################################################################
#        action - Test IP filter rule action
################################################################################
class action:
    '''Rule action.

    Verify IP filter rule action.
    Pass/Fail criteria: The IP filter must be able to block or pass packets
                        based on the rule.
    '''

    def config(self):
        self.eta = 10
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that the pass action works
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)

        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that the block action works
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, succeed=False)


################################################################################
#        direction - Test IP filter rule direction
################################################################################
class direction:
    '''Rule direction.

    Verify IP filter rule direction.
    Pass/Fail criteria: The IP filter must be able to match packets based on
                        the direction (in or out).
    '''

    def config(self):
        self.eta = 16
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        if v6:
            rulesetlist = [[['pass', 'out', 'log first', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128']]]
        else:
            rulesetlist = [[['pass', 'out', 'log first',  'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8']]]

        # Check that only output echo requests are logged
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 5, at_least = 2)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("logged input packets:      blocked 0 passed 0")
            n.r.expect_exact("logged output packets:     blocked 0 passed 1")
            n.r.wait_prompt()

        if v6:
            rulesetlist = [[['pass', 'in', 'log first', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 129']]]
        else:
            rulesetlist = [[['pass', 'in', 'log first', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 0']]]

        # Check that only input echo replies packets are logged
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 5, at_least = 2)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("logged input packets:      blocked 0 passed 1")
            n.r.expect_exact("logged output packets:     blocked 0 passed 0")
            n.r.wait_prompt()


################################################################################
#        quick - Test IP filter quick keword
################################################################################
class quick:
    '''Keword "quick".

    Verify IP filter quick keyword.
    Pass/Fail criteria: The IP filter rule parsing must immediately stop
                        when a matching rule has been found that specifies
                        the "quick" keword.
    '''

    def config(self):
        self.eta = 8
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that the quick keyword makes the first rule be chosen
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)


################################################################################
#        interface - Test IP filter interface check.
################################################################################
class interface:
    '''Keyword "on".

    Verify IP filter interface check.
    Pass/Fail criteria: The IP filter must be able to filter packets based on
                        the interface. It must be possible to invert
                        the interface specification. It must be possible to
                        wildcard the interface specification.
    '''

    def config(self):
        self.eta = 17
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        rulesetlist = [[['block', 'in', 'on', n.rifs.ifname, 'all'],
                        ['pass', 'in', 'quick', 'on', n.rifc.ifname, 'all'],
                        ['block', 'in', 'on', n.rifc.ifname, 'all']]]

        # Check that ping s->r on rifs is blocked
        # Check that ping c->r on rifc is passed
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.s.ping(n.rips, count = 1, retries = 5, succeed = False)
            n.c.ping(n.ripc, count = 1, retries = 5)

        rulesetlist = [[['pass', 'in', 'quick', 'on', 'vlan+', 'all'],
                        ['block', 'in', 'on', n.rifs.ifname, 'all'],
                        ['block', 'in', 'on', n.rifc.ifname, 'all']]]

        # Check that ping s->r on rifs is passed
        # Check that ping c->r on rifc is passed
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.s.ping(n.rips, count = 1, retries = 5)
            n.c.ping(n.ripc, count = 1, retries = 5)

        rulesetlist = [[['pass', 'out', 'quick', 'on', '! fakeifname', 'all'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that the '!' interface matches
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 5)


################################################################################
#        address - Test IP filter address scope
################################################################################
class address:
    '''Address scope.

    Verify IP filter address scope.
    Pass/Fail criteria: The IP filter must be able to filter packets based on
                        the source and destination address. It must be possible
                        to specify "any" or "me" as scope. It must be possible
                        to specify a range of addresses using a mask. It must
                        be possible to invert the address scope.
    '''

    def config(self):
        self.eta = 31
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'from any', 'to any'],
                        ['block', 'in', 'on', n.rifc.ifname, 'all']]]

        # Check that ping c->r is passed because of 'from any to any'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.ripc, count = 1, retries = 2, require_ipping = True)

        rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'from any', 'to me'],
                        ['block', 'in', 'on', n.rifc.ifname, 'all']]]

        # Check that ping c->r is passed because of 'to me'
        # Check that ping c->s fails
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.ripc, count = 1, retries = 2, require_ipping = True)
            n.c.ping(n.s.ip(), count = 1, retries = 2, succeed = False, require_ipping = True)

        rulesetlist = [[['block', 'out', 'on', n.rifc.ifname, 'from me', 'to any']]]

        # Check that ping r->c is blocked because of 'from me'
        # Check that ping r->s is passed
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.r.ping(n.c.ip(), count = 1, retries = 2, succeed = False, require_ipping = True)
            n.r.ping(n.s.ip(), count = 1, retries = 2, require_ipping = True)


        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from any', 'to ! me'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'to ! me'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, require_ipping = True)


        if v6:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'from any', 'to', n.s.ip().addr, 'icmp-type 128'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'from any', 'to', n.s.ip().addr, 'icmp-type 8'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'to n.s.ip()'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, require_ipping = True)


        if v6:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp',
                             'from any', 'to', n.s.ip().mask(n.s.ip().prefixlen).addr + '/' + str(n.s.ip().prefixlen), 'icmp-type 128'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp',
                             'from any', 'to', n.s.ip().mask(n.s.ip().prefixlen).addr + '/' + str(n.s.ip().prefixlen), 'icmp-type 8'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'to n.s.ip()/mask'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, require_ipping = True)


        if v6:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'from any', 'to', '! 1234::1234', 'icmp-type 128'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'from any', 'to', '! 1.2.3.4', 'icmp-type 8'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]

         # Check that ping c->s is passed because of 'to ! fakeip'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, require_ipping = True)

        if v6:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'from', n.c.ip().addr, 'to any', 'icmp-type 128'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'from', n.c.ip().addr, 'to any', 'icmp-type 8'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'from n.c.ip()'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, require_ipping = True)

        if v6:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'from',
                             n.c.ip().mask(n.c.ip().prefixlen).addr + '/' + str(n.c.ip().prefixlen), 'to any', 'icmp-type 128'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'from',
                             n.c.ip().mask(n.c.ip().prefixlen).addr + '/' + str(n.c.ip().prefixlen), 'to any', 'icmp-type 8'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'from n.c.ip()/mask'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, require_ipping = True)


        if v6:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'from', '! 1234::1234', 'to any', 'icmp-type 128'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'from', '! 1.2.3.4', 'to any', 'icmp-type 8'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'from ! fakeip'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, require_ipping = True)



################################################################################
#        groups - Test IP filter rule groups
################################################################################
class groups:
    '''IP filter rule groups.

    Verify IP filter rule groups support..
    Pass/Fail criteria: The IP filter must be able to use rule groups. It must
                        be possible to specify head rules which, when hit, causes
                        only the rules in a specfic group to be parsed.
    '''

    def config(self):
        self.eta = 20
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'in', 'quick', 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                        ['pass', 'in', 'quick', 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                        ['block', 'in', 'quick', 'on', n.rifs.ifname, 'all', 'head 1'],
                        ['pass', 'in', 'on', n.rifs.ifname, 'proto tcp', 'all', 'group 1'],
                        ['block', 'in', 'quick', 'on', n.rifc.ifname, 'all', 'head 2'],
                        ['pass', 'in', 'on', n.rifc.ifname, 'proto tcp', 'all', 'group 2'],
                        ['pass', 'in', 'all']]]

        # Check that TCP is passed but that UDP, RAW and ICMP echo is blocked
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, succeed = False)
            echo(n, 0, 0, 'raw', v6, succeed = False)
            echo(n, dstport, srcport, 'udp', v6, succeed = False)
            echo(n, dstport, srcport, 'tcp', v6)

        # Check that it is possible to flush a group
        n.r.send(n.r.las_prefix() +  "ipf -P r")
        n.r.expect_exact("head 2:0")
        n.r.expect_exact("group 2:1")
        n.r.expect_exact("@7 pass in all group 0:3")
        n.r.wait_prompt()
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -F g2")
        n.r.send(n.r.las_prefix() +  "ipf -P r")
        n.r.expect_exact("@5 pass in all group 0:3")
        n.r.wait_prompt()
        
        # Flush group 1
        n.r.send(n.r.las_prefix() + "ipf -Pg2")
        n.r.wait_prompt()
        n.r.send(n.r.las_prefix() + "ipf -Fg2")
        n.r.wait_prompt()
        lines = n.r.send_and_return_all(n.r.las_prefix() + "ipf -Pg2")
        if "".join(lines).find('@') != -1:
            raise test_fail('Failed to flush rules in group')


################################################################################
#        return_rst - Test IP filter return-rst feature
################################################################################
class return_rst:
    '''IP filter return-rst feature.

    Verify IP filter return-rst feature.
    Pass/Fail criteria: The IP filter must be able to block a TCP packet and
                        return a reset segment back to the sender.
    '''

    def config(self):
        self.eta = 7
        self.hosts = 3
        self.v4 = True
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                        ['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                        ['block', 'return-rst', 'in', 'on', n.rifc.ifname, 'proto tcp', 'all'],
                        ['block', 'out', 'on', n.rifs.ifname, 'proto tcp', 'all']]]

        # Check that TCP is blocked and a connection refused is returned
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            echo(n, dstport, srcport, 'tcp', v6, succeed = False, connection_refused = True)


################################################################################
#        return_icmp - Test IP filter return-icmp feature
################################################################################
class return_icmp:
    '''IP filter return-icmp feature.

    Verify IP filter return-icmp feature.
    Pass/Fail criteria: The IP filter must be able to block a packet and
                        return an icmp unreachable message back to the sender.
                        It must be possible to specify different unreachable
                        codes. It must be possible to send the unreachable
                        message with the source address taken from the firewall:
                        "return-icmp". It must be possible to send the
                        unreachable message with the source address taken from
                        the destination address of the blocked packet:
                        "return-icmp-as-dest"
    '''

    defects = ['WIND00347173']

    def config(self):
        self.eta = 10
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()


        if n.r.type == 'linux':
            if v6:
                rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                                ['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                                ['block', 'return-icmp\\(4\\)', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'], #no port v6
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]
            else:
                rulesetlist = [[['block', 'return-icmp\\(3\\)', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'], #no port v4
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]
        else:
            if v6:
                rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                                ['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                                ['block', 'return-icmp(4)', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'], #no port v6
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]
            else:
                rulesetlist = [[['block', 'return-icmp(3)', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'], #no port v4
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]

        # Check that UDP is blocked and a connection refused is returned
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            echo(n, dstport, srcport, 'udp', v6, succeed = False, connection_refused = True)

        # Network unreachable seems not to be returned to linux echoclient
        if n.s.type != 'linux' and n.c.type != 'linux':
            if v6:
                rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                                ['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                                ['block', 'return-icmp', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'],
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]
            else:
                rulesetlist = [[['block', 'return-icmp', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'],
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]

            # Check that UDP is blocked and a connection refused is returned
            for ruleset in rulesetlist:
                add_ruleset(n, ruleset, v6)
                echo(n, dstport, srcport, 'udp', v6, succeed = False, network_unreachable = True)


        if n.r.type == 'linux':
            if v6:
                rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                                ['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                                ['block', 'return-icmp-as-dest\\(4\\)', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'], #no port v6
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]
            else:
                rulesetlist = [[['block', 'return-icmp-as-dest\\(3\\)', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'], #no port v4
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]
        else:
            if v6:
                rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                                ['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                                ['block', 'return-icmp-as-dest(4)', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'], #no port v6
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]
            else:
                rulesetlist = [[['block', 'return-icmp-as-dest(3)', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'], #no port v4
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]

        # Check that UDP is blocked and a connection refused is returned
        # with the correct source address.
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

            if v6:
                proto = 'icmpv6'
                # Create a socket for icmp
                csock_icmp = n.cshell.socket('inet6', 'raw', proto)
            else:
                proto = 'icmp'
                # Create a socket for icmp
                csock_icmp = n.cshell.socket('inet', 'raw', proto)

            echo(n, dstport, srcport, 'udp', v6, succeed = False, connection_refused = True)
            log('Verify that the source address of icmp is correct (%s)' % n.s.ip().addr)
            csock_icmp.recv(exp_pattern=n.s.ip().addr, show_from_addr=True)
            csock_icmp.close()

        # Network unreachable seems not to be returned to linux echoclient
        if n.s.type != 'linux' and n.c.type != 'linux':
            if v6:
                rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 135'], #ND
                                ['pass', 'in', 'quick', 'on', n.rifc.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 136'], #ND
                                ['block', 'return-icmp-as-dest', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'],
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]
            else:
                rulesetlist = [[['block', 'return-icmp-as-dest', 'in', 'on', n.rifc.ifname, 'proto udp', 'all'],
                                ['block', 'out', 'on', n.rifs.ifname, 'proto udp', 'all']]]

                # Check that UDP is blocked and a connection refused is returned
            for ruleset in rulesetlist:
                add_ruleset(n, ruleset, v6)
                echo(n, dstport, srcport, 'udp', v6, succeed = False, network_unreachable = True)


################################################################################
#        stateful - Test IP filter stateful filtering
################################################################################
class stateful:
    '''IP filter stateful filtering.

    Verify IP filter stateful filtering support
    Pass/Fail criteria: The IP filter must be able to do stateful filtering.
                        It must be possible to block incoming UDP/TCP packets
                        unless there is a matching state entry.
    '''

    def config(self):
        self.eta = 15
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # some vxworks BSPs seem to need this (integrator1136jfs)
        check_mtu(n)

        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto udp', 'from any to any port = ' + str(dstport), 'keep state'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto tcp', 'from any to any port = ' + str(dstport), 'keep state'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'keep state'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128', 'keep state'],
                        ['block', 'in', 'on', n.rifs.ifname, 'proto udp', 'all'],
                        ['block', 'in', 'on', n.rifs.ifname, 'proto tcp', 'all'],
                        ['block', 'in', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 0'],
                        ['block', 'in', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 129']]]

        # Check that UDP, TCP and ICMP echo will generate an state entry and that the response will pass
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            echo(n, dstport + 1, srcport, 'udp', v6, succeed = False)
            # Run each traffic session twice to verify that both states are resued properly 
            for x in range(0,2):
                echo(n, dstport, srcport, 'udp', v6)
                if x == 0:  # cannot tcp to the same address/port twice or S_errno_EADDRINUSE happens
                    echo(n, dstport, srcport, 'tcp', v6)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("states added:              2")
            n.r.wait_prompt()
            n.c.ping(n.s.ip(), count = 1, retries = 2)
            n.r.send(n.r.las_prefix() +  "ipf -Ps")
            n.r.expect_exact(r"%s:%s -> %s:%s proto udp" % (n.c.ip().addr,
                                                            srcport,
                                                            n.s.ip().addr,
                                                            dstport))
            n.r.expect_exact(r"%s:%s -> %s:%s proto tcp" % (n.c.ip().addr,
                                                            srcport,
                                                            n.s.ip().addr,
                                                            dstport))
            n.r.expect_re(r"%s:[0-9]+ -> %s:[0-9]+ proto %s" % (n.c.ip().addr,
                                                                n.s.ip().addr,
                                                                IF(v6, 'ipv6-icmp', 'icmp')))


################################################################################
#        stateful - Test IP filter stateful filtering
################################################################################
class stateful_frag:
    '''IP filter stateful filtering for fragments.

    Verify IP filter stateful filtering support for fragments
    Pass/Fail criteria: The IP filter must be able to do stateful filtering for fragments.
    '''

    def config(self):
        self.eta = 15
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # some vxworks BSPs seem to need this (integrator1136jfs)
        check_mtu(n)

        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'keep state'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128', 'keep state'],
                        ['block', 'in', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 0'],
                        ['block', 'in', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 129']]]

        # Check that ICMP echo will generate an state entry and that the response will pass
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, packetsize = 2000)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Ps")
            n.r.expect_re(r"%s:[0-9]+ -> %s:[0-9]+ proto %s" % (n.c.ip().addr,
                                                                n.s.ip().addr,
                                                                IF(v6, 'ipv6-icmp', 'icmp')))

################################################################################
#        stateful - Test IP filter stateful reverse filtering
################################################################################
class stateful_reverse:
    '''IP filter stateful reverse filtering for fragments.

    Verify IP filter stateful reverse filtering support for fragments
    Pass/Fail criteria: The IP filter must be able to do stateful reverse filtering for fragments.
    '''

    def config(self):
        self.eta = 15
        self.hosts = 3
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # some vxworks BSPs seem to need this (integrator1136jfs)
        check_mtu(n)

        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'in', 'quick', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'keep state'],
                        ['pass', 'in', 'quick', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128', 'keep state']]]

        # Check that ICMP echo will generate an reversed state entry and that the response will pass
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.s.ping(n.c.ip(), count = 1, retries = 2)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Ps")
            n.r.expect_re(r"%s:[0-9]+ -> %s:[0-9]+ proto %s" % (n.c.ip().addr,
                                                                n.s.ip().addr,
                                                                IF(v6, 'ipv6-icmp', 'icmp')))


################################################################################
#        limit - Test IP filter rate limiting
################################################################################
class limit:
    '''IP filter rate limiting.

    Verify IP filter rate limiting support.
    Pass/Fail criteria: The IP filter must be able to use rate limiting. It
                        must be possible to limit packets per second, minute,
                        hour or day. It must be possible to specify a burst
                        level.
    '''

    def config(self):
        self.eta = 18
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # Ping to help NDP
        n.r.send(n.r.las_prefix() +  "ipf -D")
        n.r.wait_prompt()
        n.c.ping(n.s.ip(), count = 1, retries = 2)

        rulesetlist = [[['pass', 'out', 'log', 'limit 2/s burst 2', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8'],
                        ['pass', 'out', 'log', 'limit 2/s burst 2', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128']]]

        # Ping 40 at 4 per second and verify that only 2/s (=20) where logged */
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            for _ in range(10):
                n.c.ping(n.s.ip(), count = 4, at_least = 2, interval = 250)
                #if n.s.type == 'linux' or n.c.type == 'linux':
                time.sleep(0.25)

            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact(["logged output packets:     blocked 0 passed 18",
                              "logged output packets:     blocked 0 passed 19",
                              "logged output packets:     blocked 0 passed 20",
                              "logged output packets:     blocked 0 passed 21",
                              "logged output packets:     blocked 0 passed 22"]) # accept 18-22
            n.r.wait_prompt()


################################################################################
#        userdef - Test IP filter user defined functions
################################################################################
class userdef:
    '''IP filter user defined functions.

    Verify operation of IP filter user defined functions.
    Pass/Fail criteria: The IP filter must be able to specify a user defined
                        function and to block or pass packets based on the
                        user defined function return value.
    '''

    def config(self):
        self.eta = 10
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = False
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # Check that user defined example is available
        n.r.send(n.r.las_prefix() + "ipf -Pu")
        n.r.expect_exact_and_wait_prompt('userdef_example')

        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'userdef userdef_example match'],
                        ['block', 'out', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128', 'userdef userdef_example match']]]

        # Check that ping fails since the userdef example rule match
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2, succeed = False)

        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'userdef userdef_example nomatch'],
                        ['block', 'out', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128', 'userdef userdef_example nomatch']]]

        # Check that ping succeeds since the userdef example rule does not match
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)


################################################################################
#        rulefile - Test the load firewall rules from file feature.
################################################################################
class rulefile:
    '''Rule file.

    Verify the ability to load firewall rules from a file.
    Pass/Fail criteria: It must be possible load firewall IPv4, IPv6 and MAC rules from a file.
    '''

    def config(self):
        self.eta = 2
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        rulefilesdir = os.path.join(config.productroot, config.productpath['ipfirewall'], 'test', 'rulefiles')
        n.r.ftp_transfer(rulefilesdir)
#        n.r.send(n.r.las_prefix() +  "help")
#        n.r.wait_prompt()
#        n.r.send(n.r.las_prefix() +  "pwd")
#        n.r.wait_prompt()
#        n.r.send(n.r.las_prefix() +  "ls")
#        n.r.wait_prompt()
#        n.r.send(n.r.las_prefix() +  "cd /ram")
#        n.r.wait_prompt()
        n.r.send(n.r.las_prefix() +  "ipf -D")
        n.r.wait_prompt()
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -m -Frls")
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -Frls")
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -f " + n.r.las_prefix() + "rulefiles/fw4.cfg")
        if v6:
            n.r.expect_prompt(n.r.las_prefix() +  "ipf -6 -f "  + n.r.las_prefix() + "rulefiles/fw6.cfg")
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -m -f "  + n.r.las_prefix() + "rulefiles/fwmac.cfg")
        n.r.send(n.r.las_prefix() +  "ipf -Pr")
        n.r.expect_exact("AF_INET: @1 block in all")
        n.r.expect_exact("AF_INET: @2 pass in all")
        if v6:
            n.r.expect_exact("AF_INET6: @3 block in all")
            n.r.expect_exact("AF_INET6: @4 pass in all")
        n.r.wait_prompt()
        n.r.send(n.r.las_prefix() +  "ipf -m -Pr")
        n.r.expect_exact(["MAC:@1 block in all", "MAC: @1 block in all"])
        n.r.expect_exact(["MAC:@2 pass in all", "MAC: @2 pass in all"])
        n.r.wait_prompt()


################################################################################
#        soho - Test the Home/SOHO gateway setup.
################################################################################
class soho:
    '''Home/SOHO gateway.

    Verify operation of the example ruleset for a Home/SOHO gateway.
    Pass/Fail criteria: It must be possible initiate connections over
                        TCP/UDP and ICMP from the private to the public
                        network and receive a response. Connections
                        from the public to the private network must fail.
    '''

    def config(self):
        self.eta = 13
        self.hosts = 3
        self.v6 = False
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        tmp = n.c.ip().mask(n.c.ip().prefixlen).addr
        tmp = tmp[:tmp.rindex('.')+1] + '255'

        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['block in on', n.rifs.ifname, 'all'],
                        ['block in quick on', n.rifs.ifname, 'from', '192.168.0.0/16 to any'],
                        ['block in quick on', n.rifs.ifname, 'from', '172.16.0.0/12 to any'],
                        ['block in quick on', n.rifs.ifname, 'from', '11.0.0.0/8 to any'], #use 11 instead of 10 since we're using the 10. network
                        ['block in quick on', n.rifs.ifname, 'from', '127.0.0.0/8 to any'],
                        ['block in quick on', n.rifs.ifname, 'from', '0.0.0.0/8 to any'],
                        ['block in quick on', n.rifs.ifname, 'from', '169.254.0.0/16 to any'],
                        ['block in quick on', n.rifs.ifname, 'from', '192.0.2.0/24 to any'],
                        ['block in quick on', n.rifs.ifname, 'from', '204.152.64.0/23 to any'],
                        ['block in quick on', n.rifs.ifname, 'from', '224.0.0.0/3 to any'],
                        ['block in log quick on', n.rifs.ifname, 'from', n.c.ip().mask(n.c.ip().prefixlen).addr +'/'+ str(n.c.ip().prefixlen), 'to any'],
                        ['block in log quick on', n.rifs.ifname, 'from any to', n.c.ip().mask(n.c.ip().prefixlen).addr + '/32'],
                        ['block in log quick on', n.rifs.ifname, 'from any to',  tmp + '/32'],
                        ['pass out quick on', n.rifs.ifname, 'proto tcp/udp from', n.c.ip().mask(n.c.ip().prefixlen).addr +'/'+ str(n.c.ip().prefixlen), 'to any keep state'],
                        ['pass out quick on', n.rifs.ifname, 'proto icmp from', n.c.ip().mask(n.c.ip().prefixlen).addr +'/'+ str(n.c.ip().prefixlen), 'to any keep state']]]


        for ruleset in rulesetlist:
            # Verify that UDP passes inbound without the ruleset
            n.cshell.echoserver(proto='udp', port=dstport)
            n.sshell.echoclient(n.c.ip().addr, verify_data = True,
                                reuse_addr = True, proto = 'udp', nbuf = 1,
                                local_port = srcport, port = dstport,
                                chunk_size = 1024, succeed = True, connection_refused = False,
                                network_unreachable = False)
            n.cshell.stop_echoserver()
            # Verify that TCP passes inbound without the ruleset
            n.cshell.echoserver(proto='tcp', port=dstport)
            n.sshell.echoclient(n.c.ip().addr, verify_data = True,
                                reuse_addr = True, proto = 'tcp', nbuf = 1,
                                local_port = srcport, port = dstport,
                                chunk_size = 1024, succeed = True, connection_refused = False,
                                network_unreachable = False)
            n.cshell.stop_echoserver()
            # Verify that ICMP passes inbound without the ruleset
            n.s.ping(n.c.ip(), count = 1, retries = 2, succeed = True)
            add_ruleset(n, ruleset, v6)
            # Check that all 15 rules were added
            n.r.send(n.r.las_prefix() +  "ipf -Pr")
            n.r.expect_exact("Input:")
            n.r.expect_exact("AF_INET: @13")
            n.r.expect_exact("Output:")
            n.r.expect_exact("AF_INET: @2")
            n.r.wait_prompt()
            echo(n, dstport, srcport, 'udp', v6)
            echo(n, dstport, srcport, 'tcp', v6)
            n.c.ping(n.s.ip(), count = 1, retries = 2)
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.wait_prompt()
            # Verify that UDP fails inbound with the ruleset
            n.cshell.echoserver(proto='udp', port=dstport)
            n.sshell.echoclient(n.c.ip().addr, verify_data = True,
                                reuse_addr = True, proto = 'udp', nbuf = 1,
                                local_port = srcport, port = dstport,
                                chunk_size = 1024, succeed = False, connection_refused = False,
                                network_unreachable = False)
            n.cshell.stop_echoserver()
            # Verify that ICMP fails inbound with the ruleset
            n.s.ping(n.c.ip(), count = 1, retries = 2, succeed = False)



################################################################################
#        http_url - Test the HTTP URL filter
################################################################################
class http_url:
    '''HTTP URL filter.

    Verify operation of the HTTP URL filter.
    Pass/Fail criteria: The HTTP filter must be able to block certain URLs.
    '''

    def config(self):
        self.eta = 13
        self.hosts = 4
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.require_types = ['ipnet', 'linux', 'linux', 'linux']

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs2' + v6, hosts)

        htmldir = os.path.join(config.productroot, config.productpath['ipfirewall'], 'test', 'public_html')
        n.s.ftp_transfer(htmldir)

        # Start HTTP daemon on server
        start_apache(n)

        # Start HTTP proxy on w
        n.w.send_and_wait_prompt("/etc/init.d/privoxy start")
        time.sleep(3)
        n.w.send_and_wait_prompt('netstat -ant')
        n.w.send_and_wait_prompt('ps -auxww')

        rulesetlist = [[['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 80 userdef http_filter http_test'],
                        ['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 8118 userdef http_filter http_test']]]

        # Check the URL
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

            time.sleep(3) # wait for IPv6 address to be available

            # check that URLs may pass if no match
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.otherwebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            n.c.expect_exact('HTTP/1.1 200 OK')
            n.c.expect_exact('This is the HTTP URL filter test page')
            n.c.expect_exact('Connection closed by foreign host')
            n.c.wait_prompt()

            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/bad.html HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.otherwebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            n.c.expect_exact('HTTP/1.1 200 OK')
            n.c.expect_exact('This is the HTTP keyword filter test page')
            n.c.expect_exact('Connection closed by foreign host')
            n.c.wait_prompt()

            # check that URLs are blocked if match
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
            if i == 0:
                raise test_fail('URL not blocked!!!')
            n.c.wait_prompt()

            # check that URLs are blocked if match
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/bad.html HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
            if i == 0:
                raise test_fail('URL not blocked!!!')
            n.c.wait_prompt()

            # check that the URL matching is case insensitive
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: wWw.Somewebsite.coM\n' +
                     'Connection: close\n',
                      sudo = False)
            i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
            if i == 0:
                raise test_fail('URL not blocked!!!')
            n.c.wait_prompt()

            #verify that 3 connections were blocked
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("input  packets:            blocked 3")
            n.r.expect_exact("logged input packets:      blocked 3")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Pl")
            n.r.wait_prompt()

            if not v6:
                # check that proxy URL requests are passed if no match
                n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
                n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
                n.c.expect_exact('Escape character is')
                n.c.send('GET http://%s/~%s/ HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user) +
                         'Host: %s\n' % n.s.ip().addr +
                         'Connection: close\n',
                         sudo = False)
                n.c.expect_exact('HTTP/1.1 200 OK')
                n.c.expect_exact('This is the HTTP URL filter test page')
                n.c.expect_exact('Connection closed by foreign host')
                n.c.wait_prompt()


################################################################################
#        http_key - Test the HTTP keyword filter
################################################################################
class http_key:
    '''HTTP keyword filter.

    Verify operation of the HTTP keyword filter.
    Pass/Fail criteria: The HTTP filter must be able to block keywords in the URL.
    '''

    def config(self):
        self.eta = 13
        self.hosts = 4
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.require_types = ['ipnet', 'linux', 'linux', 'linux']

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs2' + v6, hosts)

        htmldir = os.path.join(config.productroot, config.productpath['ipfirewall'], 'test', 'public_html')
        n.s.ftp_transfer(htmldir)
        time.sleep(2)
        # Start HTTP daemon on server

        start_apache(n)

        # Start HTTP proxy on w
        n.w.send_and_wait_prompt("/etc/init.d/privoxy start")
        time.sleep(2)
        n.w.send_and_wait_prompt('netstat -ant')
        n.w.send_and_wait_prompt('ps -auxww')

        rulesetlist = [[['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 80 userdef http_filter http_key'],
                        ['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 8118 userdef http_filter http_key']]]

        # Check the URLa
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

            time.sleep(3) # wait for IPv6 address to be available

            # check that URL keywords may pass if no match
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            n.c.expect_exact('HTTP/1.1 200 OK')
            n.c.expect_exact('This is the HTTP URL filter test page')
            n.c.expect_exact('Connection closed by foreign host')
            n.c.wait_prompt()

            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/index.html HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            n.c.expect_exact('HTTP/1.1 200 OK')
            n.c.expect_exact('This is the HTTP URL filter test page')
            n.c.expect_exact('Connection closed by foreign host')
            n.c.wait_prompt()

            # check that URL keywords are blocked if match
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/bad.html HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
            if i == 0:
                raise test_fail('URL not blocked!!!')
            n.c.wait_prompt()

            # check that URL keywords are blocked if match
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/bad/test.html HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            i = n.c.expect_exact(['HTTP/1.1 404 Not Found', 'Connection closed by foreign host'])
            if i == 0:
                raise test_fail('URL not blocked!!!')
            n.c.wait_prompt()

            # check that URL keywords are case insensitive (host part)
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.BAD.com\n' +
                     'Connection: close\n',
                      sudo = False)
            i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
            if i == 0:
                raise test_fail('URL not blocked!!!')
            n.c.wait_prompt()

            # check that URL keywords are case sensitive (path part)
            n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/BAD.html HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n',
                      sudo = False)
            n.c.expect_exact('HTTP/1.1 404 Not Found') # request should not be blocked
            n.c.expect_exact('Connection closed by foreign host')
            n.c.wait_prompt()

            #verify that 3 connections were blocked
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("input  packets:            blocked 3")
            n.r.expect_exact("logged input packets:      blocked 3")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Pl")
            n.r.wait_prompt()

            if not v6:
                # check that proxy URL keywords are blocked if match
                n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
                n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
                n.c.expect_exact('Escape character is')
                n.c.send('GET http://%s/~%s/bad.html HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user) +
                         'Host: %s\n' % n.s.ip().addr +
                         'Connection: close\n',
                         sudo = False)
                i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
                if i == 0:
                    raise test_fail('URL not blocked!!!')
                n.c.wait_prompt()

                # disable firewall
                n.r.send(n.r.las_prefix() +  "ipf -D")
                n.r.wait_prompt()

                # check that proxy URL keywords are passed
                n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
                n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
                n.c.expect_exact('Escape character is')
                n.c.send('GET http://%s/~%s/bad.html HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user) +
                         'Host: %s\n' % n.s.ip().addr +
                         'Connection: close\n',
                         sudo = False)
                n.c.expect_exact('HTTP/1.1 200 OK')
                n.c.expect_exact('This is the HTTP keyword filter test page')
                n.c.expect_exact('Connection closed by foreign host')
                n.c.wait_prompt()


################################################################################
#        http_java - Test the HTTP java filter
################################################################################
class http_java:
    '''HTTP Java filter.

    Verify operation of the HTTP Java filter.
    Pass/Fail criteria: The HTTP Java filter must be able to block java files.
    '''

    def config(self):
        self.eta = 13
        self.hosts = 4
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.require_types = ['ipnet', 'linux', 'linux', 'linux']

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs2' + v6, hosts)

        htmldir = os.path.join(config.productroot, config.productpath['ipfirewall'], 'test', 'public_html')
        n.s.ftp_transfer(htmldir)

        # Start HTTP daemon on server
        start_apache(n)

        # Start HTTP proxy on w
        n.w.send_and_wait_prompt("/etc/init.d/privoxy start")
        time.sleep(3)
        n.w.send_and_wait_prompt('netstat -ant')
        n.w.send_and_wait_prompt('ps -auxww')

        rulesetlist = [[['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 80 userdef http_filter http_java'],
                        ['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 8118 userdef http_filter http_java']]]

        java_endings = ['class', 'jar', 'zip']

        # Check the URLa
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

            time.sleep(3) # wait for IPv6 address to be available

            # check that java URLs are blocked
            for ending in java_endings:
                n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
                n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
                n.c.expect_exact('Escape character is')
                n.c.send('GET /~%s/test.%s HTTP/1.1\n' % (n.s.sh.s.user, ending) +
                         'Host: www.somewebsite.com\n' +
                         'Connection: close\n',
                         sudo = False)
                i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
                if i == 0:
                    raise test_fail('URL not blocked!!!')
                n.c.wait_prompt()

            # disable firewall
            n.r.send(n.r.las_prefix() +  "ipf -D")
            n.r.wait_prompt()

            # check that java URLs are passed
            for ending in java_endings:
                n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
                n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
                n.c.expect_exact('Escape character is')
                n.c.send('GET /~%s/test.%s HTTP/1.1\n' % (n.s.sh.s.user, ending) +
                         'Host: www.somewebsite.com\n' +
                         'Connection: close\n',
                         sudo = False)
                n.c.expect_exact('HTTP/1.1 200 OK')
                n.c.expect_exact('This is the HTTP java %s filter test page' % ending)
                n.c.expect_exact('Connection closed by foreign host')
                n.c.wait_prompt()

            #verify that 3 connection were blocked
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("input  packets:            blocked %s" % len(java_endings))
            n.r.expect_exact("logged input packets:      blocked %s" % len(java_endings))
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Pl")
            n.r.wait_prompt()

            if not v6:
                # check that proxy java URLs are blocked if match
                for ending in java_endings:

                    # enable firewall
                    n.r.send(n.r.las_prefix() +  "ipf -E")
                    n.r.wait_prompt()

                    n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
                    n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
                    n.c.expect_exact('Escape character is')
                    n.c.send('GET http://%s/~%s/test.%s HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user, ending) +
                             'Host: %s\n' % n.s.ip().addr +
                             'Connection: close\n',
                             sudo = False)
                    i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
                    if i == 0:
                        raise test_fail('URL not blocked!!!')
                    n.c.wait_prompt()

                    # disable firewall
                    n.r.send(n.r.las_prefix() +  "ipf -D")
                    n.r.wait_prompt()

                    # check that proxy java URL keywords are passed
                    n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
                    n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
                    n.c.expect_exact('Escape character is')
                    n.c.send('GET http://%s/~%s/test.%s HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user, ending) +
                             'Host: %s\n' % n.s.ip().addr +
                             'Connection: close\n',
                             sudo = False)
                    n.c.expect_exact('HTTP/1.1 200 OK')
                    n.c.expect_exact('This is the HTTP java %s filter test page' % ending)
                    n.c.expect_exact('Connection closed by foreign host')
                    n.c.wait_prompt()



################################################################################
#        http_activex - Test the HTTP activex filter
################################################################################
class http_activex:
    '''HTTP Activex filter.

    Verify operation of the HTTP Activex filter.
    Pass/Fail criteria: The HTTP Activex filter must be able to block activex files.
    '''

    def config(self):
        self.eta = 13
        self.hosts = 4
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.require_types = ['ipnet', 'linux', 'linux', 'linux']

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs2' + v6, hosts)

        htmldir = os.path.join(config.productroot, config.productpath['ipfirewall'], 'test', 'public_html')
        n.s.ftp_transfer(htmldir)

        # Start HTTP daemon on server
        start_apache(n)

        # Start HTTP proxy on w
        n.w.send_and_wait_prompt("/etc/init.d/privoxy start")
        time.sleep(3)
        n.w.send_and_wait_prompt('netstat -ant')
        n.w.send_and_wait_prompt('ps -auxww')

        rulesetlist = [[['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 80 userdef http_filter http_activex'],
                        ['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 8118 userdef http_filter http_activex']]]

        activex_endings = ['ocx', 'cab']

        # Check the URLa
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

            time.sleep(3) # wait for IPv6 address to be available

            # check that activex URLs are blocked
            for ending in activex_endings:
                n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
                n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
                n.c.expect_exact('Escape character is')
                n.c.send('GET /~%s/test.%s HTTP/1.1\n' % (n.s.sh.s.user, ending) +
                         'Host: www.somewebsite.com\n' +
                         'Connection: close\n',
                         sudo = False)
                i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
                if i == 0:
                    raise test_fail('URL not blocked!!!')
                n.c.wait_prompt()

            # disable firewall
            n.r.send(n.r.las_prefix() +  "ipf -D")
            n.r.wait_prompt()

            # check that activex URLs are passed
            for ending in activex_endings:
                n.c.send('corktelnet %s 80' % n.s.ip().addr, sudo = False)
                n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
                n.c.expect_exact('Escape character is')
                n.c.send('GET /~%s/test.%s HTTP/1.1\n' % (n.s.sh.s.user, ending) +
                         'Host: www.somewebsite.com\n' +
                         'Connection: close\n',
                         sudo = False)
                n.c.expect_exact('HTTP/1.1 200 OK')
                n.c.expect_exact('This is the HTTP activex %s filter test page' % ending)
                n.c.expect_exact('Connection closed by foreign host')
                n.c.wait_prompt()

            #verify that 3 connection were blocked
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("input  packets:            blocked %s" % len(activex_endings))
            n.r.expect_exact("logged input packets:      blocked %s" % len(activex_endings))
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Pl")
            n.r.wait_prompt()

            if not v6:
                # check that proxy activex URLs are blocked if match
                for ending in activex_endings:

                    # enable firewall
                    n.r.send(n.r.las_prefix() +  "ipf -E")
                    n.r.wait_prompt()

                    n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
                    n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
                    n.c.expect_exact('Escape character is')
                    n.c.send('GET http://%s/~%s/test.%s HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user, ending) +
                             'Host: %s\n' % n.s.ip().addr +
                             'Connection: close\n',
                             sudo = False)
                    i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
                    if i == 0:
                        raise test_fail('URL not blocked!!!')
                    n.c.wait_prompt()

                    # disable firewall
                    n.r.send(n.r.las_prefix() +  "ipf -D")
                    n.r.wait_prompt()

                    # check that proxy activex URL keywords are passed
                    n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
                    n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
                    n.c.expect_exact('Escape character is')
                    n.c.send('GET http://%s/~%s/test.%s HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user, ending) +
                             'Host: %s\n' % n.s.ip().addr +
                             'Connection: close\n',
                             sudo = False)
                    n.c.expect_exact('HTTP/1.1 200 OK')
                    n.c.expect_exact('This is the HTTP activex %s filter test page' % ending)
                    n.c.expect_exact('Connection closed by foreign host')
                    n.c.wait_prompt()


################################################################################
#        http_cookie - Test the HTTP cookie filter
################################################################################
class http_cookie:
    '''HTTP Cookie filter.

    Verify operation of the HTTP Cookie filter.
    Pass/Fail criteria: The HTTP Cookie filter must be able to block Cookies.
    '''

    def config(self):
        self.eta = 13
        self.hosts = 3
        self.v6 = True # todo - get ipv6 enabled privoxy
        self.net_layout = 'ownlayout'
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.require_types = ['ipnet', 'ipnet', 'linux']

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)
        
        htmldir = os.path.join(config.productroot, config.productpath['ipfirewall'], 'test', 'public_html')
        n.s.ftp_transfer(htmldir)
        time.sleep(2)

        #Use ipnet echoserver simulates HTTP server
        # create shells
        n.sshell = n.s.ipcom_shell()
        n.sshell.echoserver(proto='tcp', port=12345, echo_once = True, reuse_addr = True)

        rulesetlist = [[['pass', 'in', 'on', n.rifc.ifname, 'proto tcp', 'from any to any port = 12345 userdef http_filter http_cookie']]]

        # Check the URLa
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

            time.sleep(3) # wait for IPv6 address to be available

            # check that the cookie is blocked. The initial cookie MARKUS_COOKIE
            # will be replaced by firewall to be dddddd: xxxxxxxxxxxxx. Then this HTTP
            # request will forward to ipnet echoserver(HTTP server)
            n.c.send('corktelnet %s 12345' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Cookie: MARKUS_COOKIE\n' +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n',
                     sudo = False)
            n.c.expect_exact('dddddd: xxxxxxxxxxxxx')
            n.c.wait_prompt()

            n.c.send('corktelnet %s 12345' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Cookie: MARKUS_COOKIE\n' +
                     'Connection: close\n',
                     sudo = False)
            n.c.expect_exact('dddddd: xxxxxxxxxxxxx')
            n.c.wait_prompt()

            n.c.send('corktelnet %s 12345' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n' +
                     'Cookie: MARKUS_COOKIE\n',
                     sudo = False)
            n.c.expect_exact('dddddd: xxxxxxxxxxxxx')
            n.c.wait_prompt()

            # disable firewall
            n.r.send(n.r.las_prefix() +  "ipf -D")
            n.r.wait_prompt()

            # check that cookies URLs are passed
            n.c.send('corktelnet %s 12345' % n.s.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.s.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET /~%s/ HTTP/1.1\n' % n.s.sh.s.user +
                     'Host: www.somewebsite.com\n' +
                     'Connection: close\n' +
                     'Cookie: MARKUS_COOKIE\n',
                     sudo = False)
            n.c.expect_exact('Cookie: MARKUS_COOKIE') # get server echo
            n.c.wait_prompt()

            # enable firewall
            n.r.send(n.r.las_prefix() +  "ipf -E")
            n.r.wait_prompt()

            n.sshell.stop_echoserver()



################################################################################
#        http_proxy - Test the HTTP Proxy filter
################################################################################
class http_proxy:
    '''HTTP Proxy filter.

    Verify operation of the HTTP Proxy filter.
    Pass/Fail criteria: The HTTP proxy filter must be able to block proxy requests.
    '''

    def config(self):
        self.eta = 13
        self.hosts = 4
        self.v6 = False # todo - get ipv6 enabled privoxy
        self.net_layout = 'ownlayout'
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.require_types = ['ipnet', 'linux', 'linux', 'linux']

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs2' + v6, hosts)

        htmldir = os.path.join(config.productroot, config.productpath['ipfirewall'], 'test', 'public_html')
        n.s.ftp_transfer(htmldir)

        # Start HTTP daemon on server
        start_apache(n)

        # Start HTTP proxy on w
        n.w.send_and_wait_prompt("/etc/init.d/privoxy start")
        time.sleep(3)
        n.w.send_and_wait_prompt('netstat -ant')
        n.w.send_and_wait_prompt('ps -auxww')

        rulesetlist = [[['block', 'return-rst', 'in', 'log on', n.rifc.ifname, 'proto tcp', 'from any to any port = 8118 userdef http_filter http_proxy']]]

        # Check the URLa
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

            time.sleep(3) # wait for IPv6 address to be available

            # check that proxy requests are blocked
            n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET http://%s/~%s/ HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user) +
                     'Host: %s\n' % n.s.ip().addr +
                     'Connection: close\n',
                      sudo = False)
            i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
            if i == 0:
                raise test_fail('URL not blocked!!!')
            n.c.wait_prompt()

            n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET http://%s/~%s/bad.html HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user) +
                     'Host: %s\n' % n.s.ip().addr +
                     'Connection: close\n',
                      sudo = False)
            i = n.c.expect_exact(['HTTP/1.1 200 OK', 'Connection closed by foreign host'])
            if i == 0:
                raise test_fail('URL not blocked!!!')
            n.c.wait_prompt()

            # disable firewall
            n.r.send(n.r.las_prefix() +  "ipf -D")
            n.r.wait_prompt()

            # check that proxy requests are passed
            n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET http://%s/~%s/ HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user) +
                     'Host: %s\n' % n.s.ip().addr +
                     'Connection: close\n',
                      sudo = False)
            n.c.expect_exact('HTTP/1.1 200 OK')
            n.c.expect_exact('This is the HTTP URL filter test page')
            n.c.expect_exact('Connection closed by foreign host')
            n.c.wait_prompt()

            n.c.send('corktelnet %s 8118' % n.w.ip().addr, sudo = False)
            n.c.expect_exact(r'Connected to %s' % n.w.ip().addr)
            n.c.expect_exact('Escape character is')
            n.c.send('GET http://%s/~%s/bad.html HTTP/1.1\n' % (n.s.ip().addr, n.s.sh.s.user) +
                     'Host: %s\n' % n.s.ip().addr +
                     'Connection: close\n',
                      sudo = False)
            n.c.expect_exact('HTTP/1.1 200 OK')
            n.c.expect_exact('This is the HTTP keyword filter test page')
            n.c.expect_exact('Connection closed by foreign host')
            n.c.wait_prompt()

            #verify that 2 connections were blocked
            n.r.send(n.r.las_prefix() +  "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("input  packets:            blocked 2")
            n.r.expect_exact("logged input packets:      blocked 2")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() +  "ipf -Pl")
            n.r.wait_prompt()

################################################################################
#        remove_rule - Test the ability to remove an IP filter rule
################################################################################
class remove_rule:
    '''Remove rule.

    Verify remove rule.
    Pass/Fail criteria: It must be possible to remove an IP filter rule
    '''

    def config(self):
        self.eta = 1
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # First disable the firewall and flush old rules
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -D")
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -Fr")

        # Add a rule
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf pass in all")
        n.r.send(n.r.las_prefix() + "ipf -Pr")
        n.r.expect_exact_and_wait_prompt("pass in all");

        # Remove the rule
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -r pass in all")
        n.r.send(n.r.las_prefix() + "ipf -Pr")
        n.r.wait_prompt_not("pass in all");

        # Flush all rules
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -Fr")

        # Re-enable the firewall
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -E")


################################################################################
#        userdef_flush - Test the ability to flush userdef functions
################################################################################
class userdef_flush:
    '''Flush userdef.

    Verify flush userdef.
    Pass/Fail criteria: It must be possible issue a flush userdef command.
                        Existing rules shall prevent the userdef function to be removed.
    '''

    def config(self):
        self.eta = 1
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # Check that user defined example is available
        n.r.send(n.r.las_prefix() + "ipf -Pu")
        n.r.expect_exact_and_wait_prompt('userdef_example')

        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'proto icmp', 'all', 'icmp-type 8', 'userdef userdef_example match'],
                        ['block', 'out', 'on', n.rifs.ifname, 'proto ipv6-icmp', 'all', 'icmp-type 128', 'userdef userdef_example match']]]

        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)

        # Check that user defined example is available
        n.r.send(n.r.las_prefix() + "ipf -Pu")
        n.r.expect_exact_and_wait_prompt('userdef_example')

        # Check that a rule refers to the userdefine example
        n.r.send(n.r.las_prefix() + "ipf -Pr")
        n.r.expect_exact_and_wait_prompt('userdef_example')

        # Try flushing the userdef example
        n.r.send(n.r.las_prefix() + "ipf -Fu")
        n.r.wait_prompt()

        # Check that user defined example is still available
        n.r.send(n.r.las_prefix() + "ipf -Pu")
        n.r.expect_exact_and_wait_prompt('userdef_example')


################################################################################
#        shell_command - Test the options of the ipfirewall shell command.
################################################################################
class shell_command:
    '''shell_command.

    Verify shell commmands.
    Pass/Fail criteria: Execute many negative inputs to ipfirewall.
                        Firewall should behave as designed.
    '''

    def config(self):
        self.eta = 1
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # Test unknown option
        n.r.send(n.r.las_prefix() + "ipf dumb")
        n.r.expect_exact_and_wait_prompt("Unknown action:")

        ### Test adding rules ###
        # Direction
        # No direction given
        n.r.send(n.r.las_prefix() + "ipf pass")
        n.r.expect_exact_and_wait_prompt("No direction specified.")
        # Unknown direction given
        n.r.send(n.r.las_prefix() + "ipf pass left")
        n.r.expect_exact_and_wait_prompt("Unknown direction:")

        # Limit
        # No value given
        n.r.send(n.r.las_prefix() + "ipf pass in limit")
        n.r.expect_exact_and_wait_prompt("No 'limit' value specified.")
        # No 'not' value given
        n.r.send(n.r.las_prefix() + "ipf pass in limit !")
        n.r.expect_exact_and_wait_prompt("No 'limit' value specified.")
        # Wrong value given
        n.r.send(n.r.las_prefix() + "ipf pass in limit dumb")
        n.r.expect_exact_and_wait_prompt("Invalid 'limit' value:")
        # Wrong time value
        n.r.send(n.r.las_prefix() + "ipf pass in limit 432/x")
        n.r.expect_exact_and_wait_prompt("Invalid 'limit' value:")
        # No burst value given
        n.r.send(n.r.las_prefix() + "ipf pass in limit 100/s")
        n.r.expect_exact_and_wait_prompt("Must specify 'burst' with 'limit'.")
        # No burst value given
        n.r.send(n.r.las_prefix() + "ipf pass in limit 100/s burst")
        n.r.expect_exact_and_wait_prompt("No 'burst' value specified.")
        # Wrong burst value given
        n.r.send(n.r.las_prefix() + "ipf pass in limit 200/s burst dumb")
        n.r.expect_exact_and_wait_prompt("Invalid 'burst' value:")

        # Interface
        # No interface given
        n.r.send(n.r.las_prefix() + "ipf pass in on")
        n.r.expect_exact_and_wait_prompt("No interface specified.")
        # No interface given
        n.r.send(n.r.las_prefix() + "ipf pass in on !")
        n.r.expect_exact_and_wait_prompt("No interface specified.")
        # Interface name longer than 16 characters
        n.r.send(n.r.las_prefix() + "ipf pass in on verylonginterfacename")
        n.r.expect_exact_and_wait_prompt("Interface name too long:")

        # pktflags
        # No pktflags given
        n.r.send(n.r.las_prefix() + "ipf pass in pktflags")
        n.r.expect_exact_and_wait_prompt("No pktflags specified.")
        # pktflags given for output rule
        n.r.send(n.r.las_prefix() + "ipf pass out pktflags")
        n.r.expect_exact_and_wait_prompt("pktflags not allowed for output rules.")
        # Faulty pktflags given 
        n.r.send(n.r.las_prefix() + "ipf pass in pktflags bad_pktflags")
        n.r.expect_exact_and_wait_prompt("Invalid pktflags:")
        # Faulty pktflags mask given 
        n.r.send(n.r.las_prefix() + "ipf pass in pktflags SNT0/TNSbad_pktmask")
        n.r.expect_exact_and_wait_prompt("Invalid pktflags:")

        # tos
        # No tos given
        n.r.send(n.r.las_prefix() + "ipf pass in tos")
        n.r.expect_exact_and_wait_prompt("No 'tos' value specified.")
        # Faulty tos given (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf pass in tos bad_tos")
        n.r.expect_exact_and_wait_prompt("Invalid 'tos' value:")
        # Faulty tos given (numeric too big)
        n.r.send(n.r.las_prefix() + "ipf pass in tos 1234 all")
        n.r.expect_exact_and_wait_prompt("Invalid 'tos' value:")
        # Faulty tos given (numeric too big)
        n.r.send(n.r.las_prefix() + "ipf pass in tos 0xFF/bad_mask all")
        n.r.expect_exact_and_wait_prompt("Invalid tos mask")

        # ttl
        # No ttl given
        n.r.send(n.r.las_prefix() + "ipf pass in ttl")
        n.r.expect_exact_and_wait_prompt("No 'ttl' value specified.")
        # Faulty ttl given (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf pass in ttl bad_ttl")
        n.r.expect_exact_and_wait_prompt("Invalid 'ttl' value:")
        # Faulty ttl given (numeric too big)
        n.r.send(n.r.las_prefix() + "ipf pass in ttl 1234 all")
        n.r.expect_exact_and_wait_prompt("Invalid 'ttl' value:")

        # Proto
        # No protocol given
        n.r.send(n.r.las_prefix() + "ipf pass in proto")
        n.r.expect_exact_and_wait_prompt("No protocol specified.")
        # No protocol given
        n.r.send(n.r.las_prefix() + "ipf pass in proto swedish")
        n.r.expect_exact_and_wait_prompt("Invalid protocol:")

        # From address
        # No address given
        n.r.send(n.r.las_prefix() + "ipf pass in")
        n.r.expect_exact_and_wait_prompt("No address specified.")
        # No address given
        n.r.send(n.r.las_prefix() + "ipf pass in from")
        n.r.expect_exact_and_wait_prompt("No address specified.")
        # Faulty address given (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf pass in from ipaddress")
        n.r.expect_exact_and_wait_prompt("Invalid address:")
        # Faulty address given (numeric)
        n.r.send(n.r.las_prefix() + "ipf pass in from 999.999.999.999")
        n.r.expect_exact_and_wait_prompt("Invalid address:")
        # Faulty mask given
        n.r.send(n.r.las_prefix() + "ipf pass in from 1.1.1.1/999")
        n.r.expect_exact_and_wait_prompt("Invalid address:")
        # No port given (tcp port)
        n.r.send(n.r.las_prefix() + "ipf pass in proto tcp from any port")
        n.r.expect_exact_and_wait_prompt("No port or operator specified.")
        # Port given for a non port protocol (icmp)
        n.r.send(n.r.las_prefix() + "ipf pass in proto icmp from any port = 432")
        n.r.expect_exact_and_wait_prompt("port specified with non-port protocol.")
        # Port given without proto keyword
        n.r.send(n.r.las_prefix() + "ipf pass in from any port = 432")
        n.r.expect_exact_and_wait_prompt("port specified without proto keyword.")
        # Faulty port given (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf pass in proto udp from any port = bad_port")
        n.r.expect_exact_and_wait_prompt("Invalid port:")
        # Faulty port given (numeric too big)
        n.r.send(n.r.las_prefix() + "ipf pass in proto udp from any port = 65536")
        n.r.expect_exact_and_wait_prompt("Invalid port:")

        # Destination address
        # No dest keyword given
        n.r.send(n.r.las_prefix() + "ipf pass in from 1.1.1.1")
        n.r.expect_exact_and_wait_prompt("No destination address specified.")
        # No address given
        n.r.send(n.r.las_prefix() + "ipf pass in from 1.1.1.1 dest to")
        n.r.expect_exact_and_wait_prompt("No destination address specified.")
        # Faulty address given (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf pass in from 1.1.1.1 to ipaddress")
        n.r.expect_exact_and_wait_prompt("Invalid address:")
        # Faulty address given (numeric)
        n.r.send(n.r.las_prefix() + "ipf pass in from 1.1.1.1 to 999.999.999.999")
        n.r.expect_exact_and_wait_prompt("Invalid address:")
        # Faulty mask given
        n.r.send(n.r.las_prefix() + "ipf pass in from 1.1.1.1 to 1.1.1.2/999")
        n.r.expect_exact_and_wait_prompt("Invalid address:")

        # icmp-type
        # No proto keyword given 
        n.r.send(n.r.las_prefix() + "ipf pass in all icmp-type")
        n.r.expect_exact_and_wait_prompt("icmp-type specified without proto keyword.")
        # Wrong protocol given 
        n.r.send(n.r.las_prefix() + "ipf pass in proto tcp all icmp-type")
        n.r.expect_exact_and_wait_prompt("icmp-type specified with non-icmp protocol.")
        # No icmp-type given
        n.r.send(n.r.las_prefix() + "ipf pass in proto icmp all icmp-type")
        n.r.expect_exact_and_wait_prompt("No icmp-type specified.")
        # Faulty icmp-type given (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf pass in proto icmp all icmp-type bad_icmp")
        n.r.expect_exact_and_wait_prompt("Invalid icmp-type:")
        # Faulty icmp-type given (numeric)
        n.r.send(n.r.las_prefix() + "ipf pass in proto icmp all icmp-type 256")
        n.r.expect_exact_and_wait_prompt("Invalid icmp-type:")
        # code without value
        n.r.send(n.r.las_prefix() + "ipf pass in proto icmp all icmp-type 1 code")
        n.r.expect_exact_and_wait_prompt("No icmp code specified.")
        # code with faulty value (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf pass in proto icmp all icmp-type 1 code bad_code")
        n.r.expect_exact_and_wait_prompt("Invalid icmp code:")
        # code with faulty value (numeric)
        n.r.send(n.r.las_prefix() + "ipf pass in proto icmp all icmp-type 1 code 256")
        n.r.expect_exact_and_wait_prompt("Invalid icmp code:")

        # flags
        # No proto given
        n.r.send(n.r.las_prefix() + "ipf pass in all flags")
        n.r.expect_exact_and_wait_prompt("flags specified without proto tcp.")
        # Wrong proto given
        n.r.send(n.r.las_prefix() + "ipf pass in proto icmp all flags")
        n.r.expect_exact_and_wait_prompt("flags specified without proto tcp.")
        # Faulty flags given
        n.r.send(n.r.las_prefix() + "ipf pass in proto tcp all flags bad_flags")
        n.r.expect_exact_and_wait_prompt("Invalid flags:")
        # Faulty mask given
        n.r.send(n.r.las_prefix() + "ipf pass in proto tcp all flags UAPRFS/bad_flags")
        n.r.expect_exact_and_wait_prompt("Invalid flags:")

        # with
        # With nothing
        n.r.send(n.r.las_prefix() + "ipf pass in all with")
        n.r.expect_exact_and_wait_prompt("Nothing following 'with' keyword.")
        # With faulty value
        n.r.send(n.r.las_prefix() + "ipf pass in all with bad_with")
        n.r.expect_exact_and_wait_prompt("Invalid 'with' option:")
        # With no nothing
        n.r.send(n.r.las_prefix() + "ipf pass in all with no")
        n.r.expect_exact_and_wait_prompt("Nothing following 'no' keyword.")
        # ipv6 with ipopts
        n.r.send(n.r.las_prefix() + "ipf -6 pass in proto icmp all with ipopts")
        n.r.expect_exact_and_wait_prompt("ipopts not relevant for this protocol family.")

        # keep
        # keep nothing
        n.r.send(n.r.las_prefix() + "ipf pass in all keep")
        n.r.expect_exact_and_wait_prompt("Nothing following 'keep' keyword.")
        # keep with faulty value
        n.r.send(n.r.las_prefix() + "ipf pass in all keep bad_keep")
        n.r.expect_exact_and_wait_prompt("Invalid keep:")

        # head
        # head nothing
        n.r.send(n.r.las_prefix() + "ipf pass in all head")
        n.r.expect_exact_and_wait_prompt("No group number specified.")
        # head with faulty group number (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf pass in all head bad_group")
        n.r.expect_exact_and_wait_prompt("Invalid group number:")
        # head with faulty group number (numeric)
        n.r.send(n.r.las_prefix() + "ipf pass in all head -1")
        n.r.expect_exact_and_wait_prompt("Invalid group number:")
        # Add same head number twice
        n.r.send(n.r.las_prefix() + "ipf pass in all head 123")
        n.r.wait_prompt()
        n.r.send(n.r.las_prefix() + "ipf pass in all head 123")
        n.r.expect_exact_and_wait_prompt("ipf :: Could not add rule.")

        # userdef
        # no userdef function given
        n.r.send(n.r.las_prefix() + "ipf pass in all userdef")
        n.r.expect_exact_and_wait_prompt("No 'userdef' function specified.")
        # userdef function name too long (>31)
        n.r.send(n.r.las_prefix() + "ipf pass in all userdef very_long_userdef_function_xxxxxxxxxxxxx")
        n.r.expect_exact_and_wait_prompt("User defined function identifier too long:")

        # Test unknown ending of command
        n.r.send(n.r.las_prefix() + "ipf pass in all bad_end")
        n.r.expect_exact_and_wait_prompt("Superfluous data at end of rule.")

        # Test "double disable"
        n.r.send(n.r.las_prefix() + "ipf -D")
        n.r.wait_prompt()
        n.r.send(n.r.las_prefix() + "ipf -D")
        n.r.expect_exact_and_wait_prompt("ipf :: firewall already disabled!")

        # Test "double enable"
        n.r.send(n.r.las_prefix() + "ipf -E")
        n.r.wait_prompt()
        n.r.send(n.r.las_prefix() + "ipf -E")
        n.r.expect_exact_and_wait_prompt("ipf :: firewall already enabled!")

        # Add rule file faulty path
        n.r.send(n.r.las_prefix() + "ipf -f bad_path")
        n.r.expect_exact_and_wait_prompt("Could not open file")

        ### Test print tables ###
        # No table given
        n.r.send(n.r.las_prefix() + "ipf -P")
        n.r.expect_exact_and_wait_prompt("Unknown switch!")
        # Faulty table given + correct tables
        n.r.send(n.r.las_prefix() + "ipf -Parslx")
        n.r.expect_exact_and_wait_prompt("Unknown table:")
        # Faulty table given
        n.r.send(n.r.las_prefix() + "ipf -Px")
        n.r.expect_exact_and_wait_prompt("Unknown table:")
        # Faulty group number given (alphabetic)
        n.r.send(n.r.las_prefix() + "ipf -Pgbad_number")
        n.r.expect_exact_and_wait_prompt("Invalid group number:")
        
        
################################################################################
#        firewall_log_time - Test the time stamp of firewall log
################################################################################
class firewall_log_time:
    '''firewall_log_time.

    Verify firewall_log_time.
    Pass/Fail criteria: change the system time and check if the firewall log time stamp correct.
    '''

    def config(self):
        self.eta = 1
        self.hosts = 3
        self.year = 2030
        self.month = 11
        self.day = 11
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = False
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        n = layout_net('rcs' + v6, hosts)

        # Check that user defined example is available
        n.s.send(n.s.las_prefix() + 'date %s-%s-%s' % (self.year, self.month, self.day))
        n.s.expect_exact_and_wait_prompt('ok')
        
        n.s.send(n.s.las_prefix() + 'ipf pass in log quick proto icmp from any to me')
        n.s.wait_prompt()
        
        n.c.send(n.c.las_prefix() + 'ping %s' % (n.s.ip().addr))
        n.c.wait_prompt()
        
        n.s.send(n.r.las_prefix() + "ipf -Pl")
        
        n.s.expect_exact_and_wait_prompt('%s/%s/%s' % (self.year, self.month, self.day))
        
