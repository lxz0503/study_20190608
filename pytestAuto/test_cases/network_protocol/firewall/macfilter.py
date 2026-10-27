#############################################################################
#
# Copyright (c) 2006-2013, 2017, 2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

'Firewall MAC Filter'

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

from util import layout_net
from ipfilter import add_ruleset
from ipfilter import echo
from ipfilter import dstport
from ipfilter import srcport

import time


################################################################################
#        check_hwvlan
################################################################################
def check_hwvlan(n):

    n.r.send(n.r.las_prefix() + "ifconfig %s" % n.rifc.parent_netif.ifname)
    i = n.r.expect_exact_and_wait_prompt(['VLAN_TXHWTAG', 'VLAN_RXHWTAG', 'MULTICAST'])
    if i > 1:
        return 'no'
    else:
        return 'yes'


################################################################################
#        syntax - Test the MAC filter rule syntax
################################################################################
class syntax:
    '''Rule syntax.

    Verify MAC filter rule syntax.
    Pass/Fail criteria: It must be possible to add all example MAC filter rules
                        from the manual without any errors both with the shell
                        command and from a rule file.
    '''

    def config(self):
        self.eta = 1
        self.hosts = 1
        self.v6 = True
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, n, v6, __):
        return


################################################################################
#        index - Test the MAC filter rule index
################################################################################
class index:
    '''Rule index.

    Verify MAC filter rule index.
    Pass/Fail criteria: It must be possible to add a MAC rule based on index in
                        the list of rules. The rule must be placed on a certain
                        index in then list and not as the last rule.
    '''

    def config(self):
        self.eta = 1
        self.hosts = 1
        self.v6 = True
        self.works_on_lkm = True
        self.works_on_iplite = False

    def test(self, log, n, v6, __):
        return


################################################################################
#        order - Test the MAC filter rule order
################################################################################
class order:
    '''Rule order.

    Verify MAC filter rule order.
    Pass/Fail criteria: The MAC filter shall parse all rules and use the last
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
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        # check that the second rule is chosen (ping will succees)
        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'all'], #match
                        ['pass', 'out', 'on', n.rifs.ifname, 'all'],  #match
                        ['pass', 'out', 'on', 'fakeifname', 'all']]]   #no match

        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        # check that the second rule is chosen (ping will fail)
        rulesetlist = [[['pass', 'out', 'on', n.rifs.ifname, 'all'],  #match
                        ['block', 'out', 'on', n.rifs.ifname, 'all'], #match
                        ['pass', 'out', 'on', 'fakeifname', 'all']]]   #no match

        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2, succeed = False)


################################################################################
#        log - Test MAC filter logging
################################################################################
class log:
    '''Logging.

    Verify MAC filter logging.
    Pass/Fail criteria: The MAC filter must be able to log matching frames. The
                        "log first" keyword must limit logging to one entry
                        per rule. The maximum number of log entries must be
                        equal to 100.
    '''

    def config(self):
        self.eta = 18
        self.hosts = 3
        self.v6 = False
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        if __['flags'].layout_net == 'bcs':
            logmactype   = '0800'
            logmaclength = '84'
            srcaddr = n.cif.mac
            logsrcaddr = n.cif.mac
        elif check_hwvlan(n) == 'no':
            logmactype   = '8100'
            logmaclength = '88'
            srcaddr = 'me'
            logsrcaddr = n.rifs.mac
        else:
            logmactype   = '0800'
            logmaclength = '84'
            srcaddr = 'me'
            logsrcaddr = n.rifs.mac


        # create shells
        n.sshell = n.s.ipcom_shell()
        n.cshell = n.c.ipcom_shell()

        rulesetlist = [[['pass', 'out', 'log', 'on', n.rifs.ifname, 'from ', srcaddr, 'to ' + n.sif.mac]]]

        # LOG all ICMP echos
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 5, at_least = 2)
            n.r.send(n.r.las_prefix() + "ipf -S")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() + "ipf -m -Pl")
            n.r.expect_exact(r"%s -> %s TYPE %s len %s" % (logsrcaddr, n.sif.mac, logmactype, logmaclength))
            n.r.expect_exact(r"%s -> %s TYPE %s len %s" % (logsrcaddr, n.sif.mac, logmactype, logmaclength))
            n.r.expect_exact(r"%s -> %s TYPE %s len %s" % (logsrcaddr, n.sif.mac, logmactype, logmaclength))
            n.r.wait_prompt()

        rulesetlist = [[['pass', 'out', 'log first', 'on', n.rifs.ifname, 'from ', srcaddr, 'to ' + n.sif.mac]]]

        # LOG the first ICMP echo
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True) # will clear statistics
            n.c.ping(n.s.ip(), count = 5, at_least = 2)
            n.r.send(n.r.las_prefix() + "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("logged output mac frames:  blocked 0 passed 1")
            n.r.wait_prompt()
            n.r.send(n.r.las_prefix() + "ipf -m -Pl")
            n.r.wait_prompt()

        rulesetlist = [[['pass', 'out', 'log', 'on', n.rifs.ifname, 'from ', srcaddr, 'to ' + n.sif.mac]]]

        # Send 105 UDP packets and LOG 100
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True) # will clear statistics
            echo(n, dstport, srcport, 'udp', v6, count = 105)
            n.r.send(n.r.las_prefix() + "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("logged output mac frames:  blocked 0 passed 100")
            n.r.wait_prompt()



################################################################################
#        action - Test MAC filter rule action
################################################################################
class action:
    '''Rule action.

    Verify MAC filter rule action.
    Pass/Fail criteria: The MAC filter must be able to block or pass packets
                        based on the rule.
    '''

    def config(self):
        self.eta = 10
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that the pass action works
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that the block action works
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2, succeed=False)



################################################################################
#        direction - Test MAC filter rule direction
################################################################################
class direction:
    '''Rule direction.

    Verify MAC filter rule direction.
    Pass/Fail criteria: The MAC filter must be able to match packets based on
                        the direction (in or out).
    '''

    def config(self):
        self.eta = 16
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        rulesetlist = [[['pass', 'out', 'log first', 'on', n.rifs.ifname, 'all']]]

        # Check that only output echo requests are logged
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 5, at_least = 2)
            n.r.send(n.r.las_prefix() + "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("logged input mac frames:   blocked 0 passed 0")
            n.r.expect_exact("logged output mac frames:  blocked 0 passed 1")
            n.r.wait_prompt()

        rulesetlist = [[['pass', 'in', 'log first', 'on', n.rifs.ifname, 'all']]]

        # Check that only input echo replies packets are logged
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 5, at_least = 2)
            n.r.send(n.r.las_prefix() + "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact("logged input mac frames:   blocked 0 passed 1")
            n.r.expect_exact("logged output mac frames:  blocked 0 passed 0")
            n.r.wait_prompt()


################################################################################
#        quick - Test MAC filter quick keword
################################################################################
class quick:
    '''Keword "quick".

    Verify MAC filter quick keyword.
    Pass/Fail criteria: The MAC filter rule parsing must immediately stop
                        when a matching rule has been found that specifies
                        the "quick" keword.
    '''

    def config(self):
        self.eta = 7
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that the quick keyword makes the first rule be chosen
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)


################################################################################
#        interface - Test MAC filter interface check.
################################################################################
class interface:
    '''Keyword "on".

    Verify MAC filter interface check.
    Pass/Fail criteria: The MAC filter must be able to filter packets based on
                        the interface. It must be possible to invert
                        the interface specification. It must be possible to
                        wildcard the interface specification.
    '''

    def config(self):
        self.eta = 16
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        if __['flags'].layout_net == 'bcs':
            rifsifname = n.bif.ifname + ' phys ' + n.rifs.ifname
            rifcifname = n.bif.ifname + ' phys ' + n.rifc.ifname
            allifs = n.bif.ifname 
        else:
            rifsifname = n.rifs.ifname
            rifcifname = n.rifc.ifname
            allifs = 'vlan+'

        rulesetlist = [[['block', 'in', 'on', rifsifname, 'all'],
                        ['pass', 'in', 'quick', 'on', rifcifname, 'all'],
                        ['block', 'in', 'on', rifcifname, 'all']]]

        # Check that ping s->r on rifs is blocked
        # Check that ping c->r on rifc is passed
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.s.ping(n.rips, count = 2, retries = 2, succeed = False)
            n.c.ping(n.ripc, count = 2, retries = 2)

        rulesetlist = [[['pass', 'in', 'quick', 'on', allifs, 'all'],
                        ['block', 'in', 'on', rifsifname, 'all'],
                        ['block', 'in', 'on', rifcifname, 'all']]]

        # Check that ping s->r on rifs is passed
        # Check that ping c->r on rifc is passed
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.s.ping(n.rips, count = 2, retries = 2)
            n.c.ping(n.ripc, count = 2, retries = 2)

        rulesetlist = [[['pass', 'out', 'quick', 'on', '! fakeifname', 'all'],
                        ['block', 'out', 'on', rifsifname, 'all']]]

        # Check that the '!' interface matches
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)


################################################################################
#        address - Test MAC filter address scope
################################################################################
class address:
    '''Address scope.

    Verify MAC filter address scope.
    Pass/Fail criteria: The MAC filter must be able to filter packets based on
                        the source and destination address. It must be possible
                        to specify "any" or "me" as scope. It must be possible
                        to specify a range of addresses using a mask. It must
                        be possible to invert the address scope.
    '''

    def config(self):
        self.eta = 33
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)
        
        if __['flags'].layout_net == 'bcs':
            rifsifname = n.bif.ifname + ' phys ' + n.rifs.ifname
            rifcifname = n.bif.ifname + ' phys ' + n.rifc.ifname
        else:
            rifsifname = n.rifs.ifname
            rifcifname = n.rifc.ifname

        rulesetlist = [[['pass', 'in', 'quick', 'on', rifcifname, 'from any', 'to any'],
                        ['block', 'in', 'on', rifcifname, 'all']]]

        # Check that ping c->r is passed because of 'from any to any'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.ripc, count = 2, retries = 2)

        rulesetlist = [[['pass', 'in', 'quick', 'on', rifcifname, 'from any', 'to me'],
                        ['block', 'in', 'on', rifcifname, 'all']]]

        # Check that ping c->r is passed because of 'to me'
        # Check that ping c->s fails
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6)
            n.c.ping(n.ripc, count = 2, retries = 2)
#            n.c.ping(n.s.ip(), count = 2, retries = 2, succeed = False)

        # Skip this for a bridge configurations
        if __['flags'].layout_net != 'bcs':
            rulesetlist = [[['block', 'out', 'on', n.rifc.ifname, 'from me', 'to any']]]

            # Check that ping r->c is blocked because of 'from me'
            # Check that ping r->s is passed
            for ruleset in rulesetlist:
                add_ruleset(n, ruleset, v6, mac = True)
                n.r.ping(n.c.ip(), count = 2, retries = 2, succeed = False)
                n.r.ping(n.s.ip(), count = 2, retries = 2)


        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from any', 'to ! me'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'to ! me'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)


        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from any', 'to', n.sif.mac],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from any', 'to', 'ff:ff:ff:ff:ff:ff'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'to n.sif.mac'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        macarray = n.sif.mac.split(':')
        macarray[5] = '00'
        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from any', 'to', ':'.join(macarray) + '/ff:ff:ff:ff:ff:00'],
                        ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from any', 'to', 'ff:ff:ff:ff:ff:ff'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'to n.sif.mac/mask'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from any', 'to', '! 12:34:56:78:9a:bc'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

         # Check that ping c->s is passed because of 'to ! fakeip'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        if __['flags'].layout_net == 'bcs':
            srcaddr = n.cif.mac
        else:
            srcaddr = n.rifs.mac 

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from', srcaddr, 'to any'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'from n.rifs.mac'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        macarray = srcaddr.split(':')
        macarray[5] = '00'
        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from', ':'.join(macarray) + '/ff:ff:ff:ff:ff:00', 'to any'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'from n.rifs.mac/mask'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'from', '! 12:34:56:78:9a:bc', 'to any'],
                        ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that ping c->s is passed because of 'from ! fakeip'
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)


################################################################################
#        mac_type - Test MAC filter mac_type keyword
################################################################################
class mac_type:
    '''MAC type keyword.

    Verify MAC filter frame type support.
    Pass/Fail criteria: The MAC filter must be able to filter packets based on
                        the frame type in the Ethernet header. It must be
                        possible to specify the MAC type both with and without
                        leading "0x"
    '''

    def config(self):
        self.eta = 14
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        if __['flags'].layout_net != 'bcs':
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 8100'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0800'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0806'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]

        # Check that a specific mac-type can be passed
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        if __['flags'].layout_net != 'bcs':
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0x8100'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0x0800'],
                            ['pass', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0x0806'],
                            ['block', 'out', 'on', n.rifs.ifname, 'all']]]


        # Check that a specific mac-type (with preceeding 0x) can be passed
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

        if __['flags'].layout_net != 'bcs':
            rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 8100'],
                            ['pass', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0800'],
                            ['block', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0806'],
                            ['pass', 'out', 'on', n.rifs.ifname, 'all']]]


        # Check that a specific mac-type can be blocked
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2, succeed = False)

        if __['flags'].layout_net != 'bcs':
            rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0x8100'],
                            ['pass', 'out', 'on', n.rifs.ifname, 'all']]]
        else:
            rulesetlist = [[['block', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0x0800'],
                            ['block', 'out', 'quick', 'on', n.rifs.ifname, 'all', 'mac-type 0x0806'],
                            ['pass', 'out', 'on', n.rifs.ifname, 'all']]]
            

        # Check that a specific mac-type (with preceeding 0x) can be blocked
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2, succeed = False)


################################################################################
#        groups - Test MAC filter rule groups
################################################################################
class groups:
    '''MAC filter rule groups.

    Verify MAC filter rule groups support..
    Pass/Fail criteria: The MAC filter must be able to use rule groups. It must
                        be possible to specify head rules which, when hit, causes
                        only the rules in a specfic group to be parsed.
    '''

    def config(self):
        self.eta = 10
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        if __['flags'].layout_net == 'bcs':
            rifsifname = n.bif.ifname + ' phys ' + n.rifs.ifname
            rifcifname = n.bif.ifname + ' phys ' + n.rifc.ifname
            allifs = n.bif.ifname 
        else:
            rifsifname = n.rifs.ifname
            rifcifname = n.rifc.ifname
            allifs = 'vlan+'

        rulesetlist = [[['block', 'in', 'quick', 'on', rifsifname, 'all', 'head 1'],
                        ['pass', 'in', 'on', rifsifname, 'all', 'group 1'],
                        ['block', 'in', 'quick', 'on', rifcifname, 'all', 'head 2'],
                        ['block', 'in', 'on', rifcifname, 'all', 'group 2'],
                        ['block', 'in', 'on ', allifs, 'all']]]

        # check that ping c->r fails
        # check that ping s->r succeeds
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.ripc, count = 2, retries = 2, succeed = False)
            n.s.ping(n.rips, count = 2, retries = 2)

        # Check that it is possible to flush a group
        n.r.send(n.r.las_prefix() +  "ipf -m -P r")
        n.r.expect_exact("head 2:0")
        n.r.expect_exact("group 2:1")
        n.r.expect_exact("@5 block in on vlan+ all group 0:1")
        n.r.wait_prompt()
        n.r.expect_prompt(n.r.las_prefix() +  "ipf -m -F g2")
        n.r.send(n.r.las_prefix() +  "ipf -m -P r")
        n.r.expect_exact("@3 block in on vlan+ all group 0:1")
        n.r.wait_prompt()


################################################################################
#        limit - Test MAC filter rate limiting
################################################################################
class limit:
    '''MAC filter rate limiting.

    Verify MAC filter rate limiting support.
    Pass/Fail criteria: The MAC filter must be able to use rate limiting. It
                        must be possible to limit packets per second, minute,
                        hour or day. It must be possible to specify a burst
                        level.
    '''

    def config(self):
        self.eta = 16
        self.hosts = 3
        self.v6 = True
        self.net_layout = 'ownlayout'
        self.works_on_lkm = True
        self.works_on_iplite = False
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        # Skip this for now
        if __['flags'].layout_net == 'bcs':
            return

        rulesetlist = [[['pass', 'out', 'log', 'limit 2/s burst 2', 'on', n.rifs.ifname, 'from me to', n.sif.mac]]]

        # Ping 40 at 4 per second and verify that only 2/s (=20) where logged */
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            for _ in range(10):
                n.c.ping(n.s.ip(), count = 4, at_least = 2, interval = 250)
                #if n.s.type == 'linux' or n.c.type == 'linux':
                time.sleep(0.25)

            n.r.send(n.r.las_prefix() + "ipf -S")
            n.r.expect_exact("FIREWALL STATISTICS:")
            n.r.expect_exact(["logged output mac frames:  blocked 0 passed 18",
                              "logged output mac frames:  blocked 0 passed 19",
                              "logged output mac frames:  blocked 0 passed 20",
                              "logged output mac frames:  blocked 0 passed 21",
                              "logged output mac frames:  blocked 0 passed 22"]) # accept 18-22
            n.r.wait_prompt()


################################################################################
#        userdef - Test MAC filter user defined functions
################################################################################
class userdef:
    '''MAC filter user defined functions.

    Verify operation of MAC filter user defined functions.
    Pass/Fail criteria: The MAC filter must be able to specify a user defined
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
        self.flags = [['layout_net', {'default':'rcs','help':'Network layout'}]]

    def test(self, log, hosts, v6, __):
        n = layout_net(__['flags'].layout_net + v6, hosts)

        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'all', 'userdef userdef_example match']]]

        # Check that ping fails since the userdef example rule match
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2, succeed = False)

        rulesetlist = [[['block', 'out', 'on', n.rifs.ifname, 'all', 'userdef userdef_example nomatch']]]

        # Check that ping succeeds since the userdef example rule does not match
        for ruleset in rulesetlist:
            add_ruleset(n, ruleset, v6, mac = True)
            n.c.ping(n.s.ip(), count = 2, retries = 2)

################################################################################
#        flush_group - Test the MAC filter flush group
################################################################################
class flush_group:
    '''Flush group.

    Verify MAC filter flush group.
    Pass/Fail criteria: It must be possible to flush all rule in a particular group
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
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -m -Fr")

        # Add a rule in the default group
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -m pass in all")
        n.r.send(n.r.las_prefix() + "ipf -m -Pr")
        n.r.expect_exact_and_wait_prompt("pass in all");

        # Add a rule in a different group
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -m block in all group 7")
        n.r.send(n.r.las_prefix() + "ipf -m -Pr")
        n.r.expect_exact_and_wait_prompt("block in all");

        # Flush the group rules
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -m -Fg7")
        n.r.send(n.r.las_prefix() + "ipf -m -Pr")
        n.r.wait_prompt_not("block in all");

        # Verify the default group rule is still there
        n.r.send(n.r.las_prefix() + "ipf -m -Pr")
        n.r.expect_exact_and_wait_prompt("pass in all");

        # Flush all rules
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -m -Fr")

        # Re-enable the firewall
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -E")


################################################################################
#        remove_rule - Test the ability to remove a MAC filter rule
################################################################################
class remove_rule:
    '''Remove rule.

    Verify remove rule.
    Pass/Fail criteria: It must be possible to remove a MAC filter rule
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
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -m -Fr")

        # Add a rule
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -m pass in all")
        n.r.send(n.r.las_prefix() + "ipf -m -Pr")
        n.r.expect_exact_and_wait_prompt("pass in all");

        # Remove the rule
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -r -m pass in all")
        n.r.send(n.r.las_prefix() + "ipf -m -Pr")
        n.r.wait_prompt_not("pass in all");

        # Flush all rules
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -m -Fr")

        # Re-enable the firewall
        n.r.send_and_wait_prompt(n.r.las_prefix() + "ipf -E")
