#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

'SNTP API'

import os
import config
import time


################################################################################
#        stop_ntpd - Stop Network Time Protocol Daemon
################################################################################
def stop_ntpd(s):
    s.send('pkill -9 ntpd')
    s.wait_prompt()


################################################################################
#        start_ntpd - Start Network Time Protocol Daemon
################################################################################
def start_ntpd(s, file):
    stop_ntpd(s)
    # try to set clock for 15 minutes then exit
    s.send('ntpd -q -c ~/ntp/' + file)
    s.wait_prompt(timeout = (15*60))
    s.send('ntpd -c ~/ntp/' + file)
    s.wait_prompt()
    s.send('ps aux')
    s.expect_exact_and_wait_prompt('ntpd')

    # try synchronizing the ntp daemon for 5 minutes
    for count in range(5 * 60 / 5):
        s.send('ntpdate -p 1 -d ' + s.ip().addr)
        i = s.expect_exact_and_wait_prompt(['no server suitable for synchronization found', 'adjust time server', 'step time server'])
        if i == 1 or i == 2:
            break
        time.sleep(5)
    else:
        raise test_fail('no server suitable for synchronization found')


################################################################################
#        copy_ntp_config - Copy ntp config files
################################################################################
def copy_ntp_config(s):
    ntpdir=os.path.join(config.productroot, config.productpath['ipsntp'], 'test', 'ntp')
    try:
        s.ftp_transfer(ntpdir)
    except:
        s.scp_recursive_upload(ntpdir)

		
################################################################################
#        ntp_verify_file
################################################################################
def ntp_verify_file(t, filename):
    lines=t.send_and_return_all('ls')
    tokens = ' '.join(lines).split()
    return filename in tokens
		
################################################################################
#        unicast - Test the SNTP unicast API
################################################################################
class unicast:
    '''SNTP unicast API.

    This tests the SNTP unicast client API.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (broadcast/multicast disabled).
    3. Use API to send sntp unicast message from target to Linux host.
    4. Verify that system time is updated on target.
    5. Redo 1-4 for ipv6'''

    def config(self):
        self.eta = 15
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
        t.send('sntp')
        t.expect_re_and_wait_prompt("The sntp command will exit with 0 on success, and non-zero on errors.")
        # get new time
        t.send('sntp -t 20 -p 123 ' + s.ip().addr)
        t.expect_exact_and_wait_prompt("System time updated")
        t.send("date")
        t.expect_re_and_wait_prompt("20[0-9][0-9]")
        stop_ntpd(s)


################################################################################
#        multicast - Test the SNTP multicast API
################################################################################
class multicast:
    '''SNTP multicast API.

    This tests the SNTP multicast client API.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (multicast enabled).
    3. Use API to wait for server multicast from Linux host.
    4. Verify that system time is updated on target.
    5. Redo 1-4 for ipv6'''

    def config(self):
        self.eta = 72
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        #self.v6 = False
        # this test case required vxsim0 (t) to use sntp client only
        # (vxsim#, old_image, new_image)
        self.restart_vxsim = (('vxsim0', 'SNTP_SERVER', 'SNTP_CLIENT'), 
                              ('vxsim0', 'SNTP_CLIENT', 'SNTP_SERVER'))

    def test(self, log, hosts, v6, __):
        if v6:
            filename = 'ntp.server.multicast.v6.conf'
            multicastaddr = 'ff05::101'
        else:
            filename = 'ntp.server.multicast.v4.conf'
            multicastaddr = '224.0.1.1'
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
        # wait for new time
        t.send('sntp -t 100 -i ' + t.netif().ifname + ' ' + multicastaddr)
        t.expect_exact("System time updated", timeout = 120)
        t.wait_prompt()
        t.send("date")
        t.expect_re_and_wait_prompt("20[0-9][0-9]")
        stop_ntpd(s)


################################################################################
#        broadcast - Test the SNTP broadcast API
################################################################################
class broadcast:
    '''SNTP broadcast API.

    This tests the SNTP broadcast client API.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (broadcast enabled).
    3. Use API to wait for server broadcast from Linux host.
    4. Verify that system time is updated on target'''

    def config(self):
        self.eta = 72
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
        s.send_and_return_all('cat ntp/%s | sed "s:255.255.255.255:%s:" > ntp/%s.netbroadcast' % (filename, s.ip().broadcast(s.ip().prefixlen).addr, filename))
        start_ntpd(s, filename + ".netbroadcast");

        # set invalid time
        t.send("date 1999-01-02")
        t.expect_exact_and_wait_prompt("ok", timeout = 300) # extra long timeout on first date command
        t.send("date")
        t.expect_re_and_wait_prompt("1999")
        # wait for new time
        t.send('sntp -t 150 -b')
        t.expect_exact("System time updated", timeout = 200)
        t.wait_prompt()
        t.send("date")
        t.expect_re_and_wait_prompt("20[0-9][0-9]")
        stop_ntpd(s)
