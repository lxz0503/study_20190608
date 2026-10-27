#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

'SNTP client'

from api import stop_ntpd
from api import start_ntpd
from api import copy_ntp_config
import time


################################################################################
#        unicast - Test the SNTP unicast client
################################################################################
class unicast:
    '''SNTP unicast client.

    This tests the SNTP unicast client.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (broadcast/multicast disabled).
    3. Use SNTP client daemon to send sntp unicast message from target to Linux host.
    4. Verify that system time is updated on target.
    5. Redo 1-4 for ipv6'''

    def config(self):
        self.eta = 55
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        #self.v6 = False

    def test(self, log, hosts, v6, __):
        filename = 'ntp.server.unicast.conf'
        t,z,s = hosts
        t.stop_proc('ipsntp');
        t.ping(s.ip().addr, count = 2, retries = 5)
        copy_ntp_config(s)
        start_ntpd(s, filename);
        # set invalid time
        t.send("date 1999-01-02")
        t.expect_exact_and_wait_prompt("ok")
        t.send("date")
        t.expect_re_and_wait_prompt("1999")
        # start sntp client daemon with primary server
        t.set_sysvar('ipsntp.client.poll.count', '1')
        t.set_sysvar('ipsntp.client.poll.timeout', '2')
        t.set_sysvar('ipsntp.client.poll.interval', '5')
        if v6:
            t.set_sysvar('ipsntp.client.primary.addr6', s.ip().addr)
            t.unset_sysvar('ipsntp.client.backup.addr6', cleanup = True)
            t.unset_sysvar('ipsntp.client.primary.addr', cleanup = True)
            t.unset_sysvar('ipsntp.client.backup.addr', cleanup = True)
        else:
            t.set_sysvar('ipsntp.client.primary.addr', s.ip().addr)
            t.unset_sysvar('ipsntp.client.backup.addr', cleanup = True)
            t.unset_sysvar('ipsntp.client.primary.addr6', cleanup = True)
            t.unset_sysvar('ipsntp.client.backup.addr6', cleanup = True)
        t.send_and_wait_prompt('sysvar list ipsntp')
        t.start_proc('ipsntp')
        # sleep for 20 seconds while time is updated
        time.sleep(20)
        t.send("date")
        t.expect_re_and_wait_prompt("20[0-9][0-9]")
        t.stop_proc('ipsntp');
        # set invalid time
        t.send("date 1999-01-02")
        t.expect_exact_and_wait_prompt("ok")
        t.send("date")
        t.expect_re_and_wait_prompt("1999")
        # start sntp client daemon with secondary server
        if v6:
            t.set_sysvar('ipsntp.client.backup.addr6', s.ip().addr)
            t.unset_sysvar('ipsntp.client.primary.addr6', cleanup = True)
            t.unset_sysvar('ipsntp.client.primary.addr', cleanup = True)
            t.unset_sysvar('ipsntp.client.backup.addr', cleanup = True)
        else:
            t.set_sysvar('ipsntp.client.backup.addr', s.ip().addr)
            t.unset_sysvar('ipsntp.client.primary.addr', cleanup = True)
            t.unset_sysvar('ipsntp.client.primary.addr6', cleanup = True)
            t.unset_sysvar('ipsntp.client.backup.addr6', cleanup = True)
        t.send_and_wait_prompt('sysvar list ipsntp')
        t.start_proc('ipsntp')
        # sleep for 40 seconds while time is updated
        time.sleep(40)
        t.send("date")
        t.expect_re_and_wait_prompt("20[0-9][0-9]")
        stop_ntpd(s)


################################################################################
#        multicast - Test the SNTP multicast client
################################################################################
class multicast:
    '''SNTP multicast client.

    This tests the SNTP multicast client.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (multicast enabled).
    3. Use SNTP multicast client to wait for server multicast from Linux host.
    4. Verify that system time is updated on target.
    5. Redo 1-4 for ipv6'''

    def config(self):
        self.eta = 95
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        #self.v6 = False

    def test(self, log, hosts, v6, __):
        if v6:
            filename = 'ntp.server.multicast.v6.conf'
        else:
            filename = 'ntp.server.multicast.v4.conf'
        t,z,s = hosts
        t.stop_proc('ipsntp');
        t.ping(s.ip().addr, count = 2, retries = 5)
        copy_ntp_config(s)
        start_ntpd(s, filename);
        # set invalid time
        t.send("date 1999-01-02")
        t.expect_exact_and_wait_prompt("ok")
        t.send("date")
        t.expect_re_and_wait_prompt("1999")
        # start sntp client daemon in multicast mode
        t.set_sysvar('ipsntp.client.poll.interval', '0')
        if v6:
            t.set_sysvar('ipsntp.client.multi.if6', t.netif().ifname)
            t.set_sysvar('ipsntp.client.multi.addr6', 'ff05::101')
            t.unset_sysvar('ipsntp.client.multi.if', cleanup = True)
            t.unset_sysvar('ipsntp.client.multi.addr', cleanup = True)
        else:
            t.set_sysvar('ipsntp.client.multi.if', t.netif().ifname)
            t.set_sysvar('ipsntp.client.multi.addr', '224.0.1.1')
            t.unset_sysvar('ipsntp.client.multi.if6', cleanup = True)
            t.unset_sysvar('ipsntp.client.multi.addr6', cleanup = True)
        t.send_and_wait_prompt('sysvar list ipsntp')
        t.start_proc('ipsntp')
        # sleep for 150 seconds while time is updated
        time.sleep(150)
        t.send("date")
        t.expect_re_and_wait_prompt("20[0-9][0-9]")
        stop_ntpd(s)


################################################################################
#        broadcast - Test the SNTP broadcast client
################################################################################
class broadcast:
    '''SNTP broadcast client.

    This tests the SNTP broadcast client.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (broadcast enabled).
    3. Use SNTP broadcast client to wait for server broadcast from Linux host.
    4. Verify that system time is updated on target'''

    def config(self):
        self.eta = 95
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        self.v6 = False

    def test(self, log, hosts, v6, __):
        filename = 'ntp.server.broadcast.conf'
        t,z,s = hosts
        t.stop_proc('ipsntp');
        t.ping(s.ip().addr, count = 2, retries = 5)
        copy_ntp_config(s)

        ##
        s.send_and_return_all('cat ntp/%s | sed "s:255.255.255.255:%s:" > ntp/%s.clientbroadcast' % (filename, s.ip().broadcast(s.ip().prefixlen).addr, filename))
        start_ntpd(s, filename + ".clientbroadcast");

        # set invalid time
        t.send("date 1999-01-02")
        t.expect_exact_and_wait_prompt("ok")
        t.send("date")
        t.expect_re_and_wait_prompt("1999")
        # start sntp client daemon in multicast mode
        t.set_sysvar('ipsntp.client.poll.interval', '0')
        if v6:
            t.set_sysvar('ipsntp.client.multi.if6', t.netif().ifname)
            t.set_sysvar('ipsntp.client.multi.addr6', 'ff05::101')
            t.unset_sysvar('ipsntp.client.multi.if', cleanup = True)
            t.unset_sysvar('ipsntp.client.multi.addr', cleanup = True)
        else:
            t.set_sysvar('ipsntp.client.multi.if', t.netif().ifname)
            t.set_sysvar('ipsntp.client.multi.addr', '224.0.1.1')
            t.unset_sysvar('ipsntp.client.multi.if6', cleanup = True)
            t.unset_sysvar('ipsntp.client.multi.addr6', cleanup = True)
        t.send_and_wait_prompt('sysvar list ipsntp')
        t.start_proc('ipsntp')
        # sleep for 150 seconds while time is updated
        time.sleep(150)
        t.send("date")
        t.expect_re_and_wait_prompt("20[0-9][0-9]")
        stop_ntpd(s)


