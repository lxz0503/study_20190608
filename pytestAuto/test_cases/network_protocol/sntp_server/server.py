#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

'SNTP server'

from api import stop_ntpd
from api import start_ntpd
from api import copy_ntp_config
from api import ntp_verify_file
import time

################################################################################
#        unicast - Test the SNTP unicast server mode
################################################################################
class unicast:
    '''SNTP unicast server.

    This tests the SNTP unicast server mode.
    1. Set incorrect system time on Linux host.
    2. Start sntp daemon on target (broadcast disabled).
    3. Send ntp message from Linux host to the unicast server.
    4. Verify that system time is updated on Linux host.
    5. Redo 1-4 for ipv6'''

    def config(self):
        self.eta = 102
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        #self.v6 = False

    def test(self, log, hosts, v6, __):
        filename = 'ntp.server.unicast.conf'
        t,z,c = hosts
        t.stop_proc('ipsntp');
        t.ping(c.ip().addr, count = 2, retries = 5)
        copy_ntp_config(c)
        start_ntpd(c, filename);
        # get time so that server will have a reasonable date
        t.send('sntp -t 20 ' + c.ip().addr)
        t.expect_exact_and_wait_prompt("System time updated")
        t.send("date")
        t.expect_re_and_wait_prompt("20[0-9][0-9]")
        stop_ntpd(c)
        # start sntp server daemon in unicast mode
        t.set_sysvar('ipsntp.daemon.mode', 's')
        t.set_sysvar('ipsntp.server.mcast.interval', '0')
        t.send_and_wait_prompt('sysvar list ipsntp')
        t.start_proc('ipsntp')
        t.send('sntp -r')
        t.expect_exact_and_wait_prompt("Server reference set.")
        t.send('sntp -s')
        t.expect_exact_and_wait_prompt("Server precision set.")
        # get time on linux host
        c.send("ntpdate -p 1 -d " + t.ip().addr)
        c.expect_exact_and_wait_prompt(['adjust time server', 'step time server'])


################################################################################
#        multicast - Test the SNTP multicast server mode
################################################################################
class multicast:
    '''SNTP multicast server.

    This tests the SNTP multicast server mode.
    1. Set incorrect system time on Linux host.
    2. Start sntp daemon on target (multicast enabled).
    3. Wait for server broadcast from target.
    4. Verify that system time is updated on Linux host.
    5. Redo 1-4 for ipv6'''

    def config(self):
        self.eta = 17
        self.hosts = 2
        self.require_types = ['ipnet', 'ipnet']
        self.works_on_lkm = True
        self.works_on_iplite = True
        # this test case required vxsim1 (z) to use sntp client only
        # (vxsim#, old_image, new_image)
        self.restart_vxsim = (('vxsim1', 'SNTP_SERVER', 'SNTP_CLIENT'), 
                              ('vxsim1', 'SNTP_CLIENT', 'SNTP_SERVER'))


    def test(self, log, hosts, v6, __):
        t,z = hosts
        
        t.send("sntp -v")
        i = t.expect_exact_and_wait_prompt(['ipsntp-any-p6_5_0_2', 'ipsntp-any-p6_5_0_3', 'ipsntp-any-p6_5_0_4', 'INTERPEAK_COPYRIGHT_STRING', 'Copyright'])
        if i <= 2:
            return 'skipped'
        t.stop_proc('ipsntp');
        z.stop_proc('ipsntp');
        # start sntp server daemon in multicast mode
        t.send("date 2007-01-02")
        t.expect_exact_and_wait_prompt("ok")
        t.set_sysvar('ipsntp.daemon.mode', 's')
        t.set_sysvar('ipsntp.server.mcast.interval', '16')
        if v6:
            t.set_sysvar('ipsntp.server.mcast.addr6', 'ff05::101%' + t.netif().ifname)
        else:
            t.set_sysvar('ipsntp.server.mcast.addr', '224.0.1.1%' + t.netif().ifname)
        t.send_and_wait_prompt('sysvar list ipsntp')
        t.start_proc('ipsntp')
        t.send('sntp -r')
        t.expect_exact_and_wait_prompt("Server reference set.")
        # set invalid time
        z.send("date 2006-01-02")
        z.expect_exact_and_wait_prompt("ok")
        z.send("date")
        z.expect_re_and_wait_prompt("2006")
        # wait for new mulitcasted time
        if v6:
            z.send('sntp -t 100 -i ' + z.netif().ifname + ' ff05::101')
        else:
            z.send('sntp -t 100 -i ' + z.netif().ifname + ' 224.0.1.1')
        z.expect_exact("System time updated", timeout = 300)
        z.wait_prompt()
        z.send("date")
        z.expect_exact(["JAN", "Jan"])
        z.expect_exact("2007")
        z.wait_prompt()


################################################################################
#        broadcast - Test the SNTP broadcast server mode
################################################################################
class broadcast:
    '''SNTP broadcast server.

    This tests the SNTP broadcast server mode.
    1. Set incorrect system time on Linux host.
    2. Start sntp daemon on target (broadcast enabled).
    3. Wait for server broadcast from target.
    4. Verify that system time is updated on Linux host.'''

    def config(self):
        self.eta = 17
        self.hosts = 2
        self.require_types = ['ipnet', 'ipnet']
        self.works_on_lkm = True
        self.works_on_iplite = True
        self.v6 = False

    def test(self, log, hosts, v6, __):
        t,z = hosts
        t.stop_proc('ipsntp');
        z.stop_proc('ipsntp');
        # start sntp server daemon in broadcast mode
        t.send("date 2007-01-02")
        t.expect_exact_and_wait_prompt("ok")
        t.set_sysvar('ipsntp.daemon.mode', 's')
        t.set_sysvar('ipsntp.server.mcast.interval', '16')
        t.set_sysvar('ipsntp.server.mcast.addr', '255.255.255.255')
        t.send_and_wait_prompt('sysvar list ipsntp')
        t.start_proc('ipsntp')
        t.send('sntp -r')
        t.expect_exact_and_wait_prompt("Server reference set.")
        # set invalid time
        z.send("date 2006-01-02")
        z.expect_exact_and_wait_prompt("ok")
        z.send("date")
        z.expect_re_and_wait_prompt("2006")
        # wait for new broadcasted time
        z.send('sntp -t 100 -b')
        z.expect_exact("System time updated", timeout = 300)
        z.wait_prompt()
        z.send("date")
        z.expect_exact(["JAN", "Jan"])
        z.expect_exact("2007")
        z.wait_prompt()


################################################################################
#        leapsecond - Test the SNTP server with leapsecond enabled
################################################################################
class leapsecond:
    '''SNTP server with leapsecond.

    This tests the SNTP server mode with leapsecond enabled.
    1. Set leapsecond file in target t in server mode
    2. set no-leapsecond file in target z in server mode
    3. In target z, update time with target t.
    4. after the leapsecond day is gone, checking the time diff.'''

    def config(self):
        self.eta = 300
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        self.v6  = False # ATFTPD doesnt support v6 yet.

    def test(self, log, hosts, v6, __):
        filename = 'leap-seconds.3629404800'
        t,z,c = hosts
        t.stop_proc('ipsntp');
        z.stop_proc('ipsntp');
        t.ping(z.ip().addr, count = 2, retries = 5)
        copy_ntp_config(c)
        #copy leapsecond file to target t
        c.send_and_wait_prompt('pkill -9 in.tftpd')
        c.send_and_wait_prompt('in.tftpd --daemon ~/ntp/')
        c.send('ps aux')
        c.expect_exact_and_wait_prompt('in.tftpd')
        t.ping(c.ip().addr, count = 2, retries = 5)
        t.send_and_wait_prompt('tftp ' + c.ip().addr + ' get ' + filename)
        if not ntp_verify_file(t, filename):
            raise test_fail('leapsecond file is not existed.')
        #start sntp server daemon in unicast mode
        t.set_sysvar('ipsntp.daemon.mode', 's')
        t.set_sysvar('ipsntp.server.leapsecond_filename', filename)
        z.set_sysvar('ipsntp.daemon.mode', 's')
        #hardcoded to set the target t local time to be 1435708680UL 23:58:00 Jun.30 2015
        #It is an internal sntp cmd option.
        t.send('sntp -l')
        t.expect_exact_and_wait_prompt("time: 55932d08.0")
        #start sntp server in both target t and z
        t.start_proc('ipsntp')
        z.start_proc('ipsntp')
        #wait for 3mins and then check the leapsecond is added or not
        time.sleep(180)
        t.send('sntp -d -w ' + z.ip().addr)
        t.expect_exact_and_wait_prompt("leapsecond is handled correctly!")