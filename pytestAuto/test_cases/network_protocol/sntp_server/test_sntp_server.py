#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/22/2024 4:30 PM
@file:test_sntp_client.py
"""
import time
import allure
import pytest
import sys


from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage


def stop_ntpd(ntps, prompt):
    ntps.sendAndExpect('pkill -9 ntpd', prompt)


def start_ntpd(ntps, file_name, prompt, ip):
    stop_ntpd(ntps, prompt)

    # try to set clock for 15 minutes then exit
    ntps.sendAndExpect('ntpd -q -c ~/ntp/' + file_name, prompt, timeout=900)
    ntps.sendAndExpect('ntpd -c ~/ntp/' + file_name, prompt, timeout=60)
    res = '\n'.join(ntps.sendAndReturnAll('ps aux', prompt))
    if 'ntpd' not in res:
        log.error('Failed to start ntpd')
        assert False

    # try synchronizing the ntp daemon for 5 minutes
    for _ in range(5 * 60 / 5):
        ntps.send('ntpdate -p 1 -d ' + ip)
        i = ntps.expect(
            ['no server suitable for synchronization found', 'adjust time server', 'step time server'])
        if i == 1 or i == 2:
            break
        time.sleep(5)
    else:
        log.error('no server suitable for synchronization found')
        assert False


class TestSNTPServer(object):
    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-sntp-server/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'ipsntp.sntpserver'
        self.lxprompt = r'ubuntu@ubuntu:~\$ '  # xiaozhan, must has \$
        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 3)]
        [x.boot(vximage) for x in self.vx_targets]

        lximage = LinuxImage('/home/xli3/pytestAuto/config/focal-server-cloudimg-amd64.img')
        self.t_lx = QemuTarget('QEMU-LX-1', logFile='linuxqemu.log')
        self.t_lx.boot(lximage)

        # qemu VxWorks
        self.t1, self.t2 = self.vx_targets
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::10 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.10 prefixlen 24 up', self.vxprompt)

        self.t2.sendAndExpect('cmd', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet6 add 2000::20 prefixlen 64 up', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet add 10.236.1.20 prefixlen 24 up', self.vxprompt)

        self.t1_ip, self.t1_ip6 = self.t1.get_ip()
        self.t2_ip, self.t2_ip6 = self.t2.get_ip()
        self.lx_ip, self.lx_ip6 = self.t_lx.get_ip()

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_server_unicast(self, version):
        with allure.step('Test the SNTP unicast server'):
            """SNTP unicast server.
            This tests the SNTP unicast server mode.
            1. Set incorrect system time on Linux host.
            2. Start sntp daemon on target (broadcast disabled).
            3. Send ntp message from Linux host to the unicast server.
            4. Verify that system time is updated on Linux host.
            5. Redo 1-4 for ipv6"""
            ntpc, ntps = self.t1, self.t_lx  # t z s
            name = 'server_unicast'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.unicast.conf'
            try:
                if version == 'IPv6':
                    ntpc_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                ntpc.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                # get time so that server will have a reasonable date
                ntpc.send('sntp -t 20 ' + ntps_ip)
                ntpc.expect("System time updated")
                ntpc.send("date")
                ntpc.expect(r"20[0-9][0-9]")
                stop_ntpd(ntps, self.lxprompt)

                # start sntp server daemon in unicast mode
                ntpc.sendAndExpect('sysvar set -co ipsntp.daemon.mode "s"', self.vxprompt)
                ntpc.sendAndExpect('sysvar set -co ipsntp.server.mcast.interval "0"', self.vxprompt)
                ntpc.sendAndExpect('sysvar list ipsntp', self.vxprompt)
                ntpc.sendAndExpect('ipd start ipsntp', self.vxprompt)
                ntpc.send('sntp -r')
                ntpc.expect("Server reference set.")
                ntpc.send('sntp -s')
                ntpc.expect("Server precision set.")
                # get time on linux host
                ntps.send("ntpdate -p 1 -d " + ntpc_ip)
                ntps.expect(['adjust time server', 'step time server'])

            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_server_multicast(self, version):
        with allure.step('Test the SNTP multicast server'):
            """SNTP multicast server.
            This tests the SNTP multicast server mode.
            1. Set incorrect system time on Linux host.
            2. Start sntp daemon on target (multicast enabled).
            3. Wait for server broadcast from target.
            4. Verify that system time is updated on Linux host.
            5. Redo 1-4 for ipv6"""
            ntps, ntpc = self.t1, self.t2  # t z s
            name = 'server_multicast'
            case_name = self.module + '.' + name + '-' + version
            try:
                ntps.send("sntp -v")
                i = ntps.expect(
                    ['ipsntp-any-p6_5_0_2', 'ipsntp-any-p6_5_0_3', 'ipsntp-any-p6_5_0_4', 'INTERPEAK_COPYRIGHT_STRING',
                     'Copyright'])
                if i <= 2:
                    log.error('error infor', i)
                    assert False
                ntps.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                ntpc.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # start sntp server daemon in multicast mode
                ntps.sendAndExpect("date 2007-01-02", "ok")
                ntps.sendAndExpect('sysvar set -co ipsntp.daemon.mode "s"', self.vxprompt)
                ntps.sendAndExpect('sysvar set -co ipsntp.server.mcast.interval "16"', self.vxprompt)
                if version == 'IPv6':
                    value = 'ff05::101%' + 'eth0'
                    cmd = '%s "%s"' % ('sysvar set -co ipsntp.server.mcast.addr6', value)
                    ntps.sendAndExpect(cmd, self.vxprompt)
                else:
                    value = '224.0.1.1%' + 'eth0'
                    cmd = '%s "%s"' % ('sysvar set -co ipsntp.server.mcast.addr', value)
                    ntps.sendAndExpect(cmd, self.vxprompt)
                ntps.sendAndExpect('sysvar list ipsntp', self.vxprompt)
                ntps.sendAndExpect('ipd start ipsntp', self.vxprompt)
                ntps.send('sntp -r')
                ntps.expect("Server reference set.")
                # set invalid time
                ntpc.sendAndExpect("date 2006-01-02", "ok")
                ntpc.sendAndExpect("date", "2006")
                # wait for new mulitcasted time
                if version == 'IPv6':
                    ntpc.send('sntp -t 100 -i ' + 'eth0' + ' ff05::101')
                else:
                    ntpc.send('sntp -t 100 -i ' + 'eth0' + ' 224.0.1.1')
                ntpc.expect("System time updated", timeout=300)
                ntpc.expect(self.vxprompt)
                ntpc.send("date")
                ntpc.expect(["JAN", "Jan"])
                ntpc.expect("2007")
                ntpc.expect(self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_server_broadcast(self, version):
        with allure.step('Test the SNTP broadcast server'):
            """SNTP broadcast server.
            This tests the SNTP broadcast server mode.
            1. Set incorrect system time on Linux host.
            2. Start sntp daemon on target (broadcast enabled).
            3. Wait for server broadcast from target.
            4. Verify that system time is updated on Linux host."""
            ntps, ntpc = self.t1, self.t2
            name = 'server_multicast'
            case_name = self.module + '.' + name + '-' + version
            try:
                ntps.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                ntpc.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # start sntp server daemon in broadcast mode
                ntps.sendAndExpect("date 2007-01-02", "ok")
                ntps.sendAndExpect('sysvar set -co ipsntp.daemon.mode "s"', self.vxprompt)
                ntps.sendAndExpect('sysvar set -co ipsntp.server.mcast.interval "16"', self.vxprompt)
                ntps.sendAndExpect('ipsntp.server.mcast.addr "255.255.255.255"', self.vxprompt)
                ntps.sendAndExpect('sysvar list ipsntp', self.vxprompt)
                ntps.sendAndExpect('ipd start ipsntp', self.vxprompt)
                ntps.send('sntp -r')
                ntps.expect("Server reference set.")
                # set invalid time
                ntpc.sendAndExpect("date 2006-01-02", "ok")
                ntpc.sendAndExpect("date", "2006")
                # wait for new broadcasted time
                ntpc.send('sntp -t 100 -b')
                ntpc.expect("System time updated", timeout=300)
                ntpc.expect(self.vxprompt)
                ntpc.send("date")
                ntpc.expect(["JAN", "Jan"])
                ntpc.expect("2007")
                ntpc.expect(self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_server_leapsecond(self, version):
        with allure.step('Test the SNTP server leapsecond'):
            """SNTP server with leapsecond.
            This tests the SNTP server mode with leapsecond enabled.
            1. Set leapsecond file in target t in server mode
            2. set no-leapsecond file in target z in server mode
            3. In target z, update time with target t.
            4. after the leapsecond day is gone, checking the time diff."""
            ntps1, ntps2 = self.t1, self.t2
            name = 'server_leapsecond'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'leap-seconds.3629404800'
            try:
                ntps1.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                ntps2.sendAndExpect('ipd kill ipsntp', self.vxprompt)

                # start sntp server daemon in unicast mode
                ntps1.sendAndExpect('sysvar set -co ipsntp.daemon.mode "s"', self.vxprompt)
                cmd = '%s "%s"' % ('sysvar set -co ipsntp.server.leapsecond_filename', file_name)
                ntps1.sendAndExpect(cmd, self.vxprompt)

                ntps2.sendAndExpect('sysvar set -co ipsntp.daemon.mode "s"', self.vxprompt)
                # hardcoded to set the target t local time to be 1435708680UL 23:58:00 Jun.30 2015
                # It is an internal sntp cmd option.
                ntps1.send('sntp -l')
                ntps1.expect("time: 55932d08.0")
                # start sntp server in both target t and z
                ntps1.sendAndExpect('ipd start ipsntp', self.vxprompt)
                ntps2.sendAndExpect('ipd start ipsntp', self.vxprompt)
                # wait for 3mins and then check the leapsecond is added or not
                time.sleep(180)
                if version == 'IPv6':
                    ntps2_ip = self.t2_ip6
                else:
                    ntps2_ip = self.t2_ip
                ntps1.send('sntp -d -w ' + ntps2_ip)
                ntps1.expect("leapsecond is handled correctly!")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    def teardown_class(self):
        # clean up vxworks
        for t in self.vx_targets:
            t.cleanup()
            t.logFile.close()
        # clean up linux----xiaozhan, this must be after vxworks cleanup
        self.t_lx.cleanup()
        self.t_lx.logFile.close()
        # process self.result ----store result,upload to Database or sth like that
        for i in self.result:
            if i[1] == 'PASS':
                self.pass_num += 1
            else:
                self.fail_num += 1
        log.info(self.result)
        log.info(f'total:{len(self.result)}, pass:{self.pass_num}, fail:{self.fail_num}')
