#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/17/2024 4:30 PM
@file:test_sntp_client.py
"""
import time
import allure
import pytest
import sys
import os
import re
from datetime import date, datetime, timedelta


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


class TestSNTPClient(object):
    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-sntp-client/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'ipsntp.sntpclient'
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
    def test_sntp_client_unicast(self, version):
        with allure.step('Test the SNTP unicast client'):
            """SNTP unicast client.
                This tests the SNTP unicast client.
                1. Set incorrect system time on target.
                2. Start Linux ntpd (broadcast/multicast disabled).
                3. Use SNTP client daemon to send sntp unicast message from target to Linux host.
                4. Verify that system time is updated on target.
                5. Redo 1-4 for ipv6"""
            ntpc1, ntpc2, ntps = self.t1, self.t2, self.t_lx  # t z s
            name = 'client_unicast'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.unicast.conf'
            try:
                if version == 'IPv6':
                    ntpc1_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc1_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                ntpc1.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                # set invalid time
                ntpc1.sendAndExpect("date 1999-01-02", "ok")
                ntpc1.sendAndExpect("date", "1999")
                # start sntp client daemon with primary server
                ntpc1.sendAndExpect('sysvar set -co ipsntp.client.poll.count "1"', self.vxprompt)
                ntpc1.sendAndExpect('sysvar set -co ipsntp.client.poll.timeout "2"', self.vxprompt)
                ntpc1.sendAndExpect('sysvar set -co ipsntp.client.poll.interval "5"', self.vxprompt)
                if version == 'IPv6':
                    name = 'sysvar set -co ipsntp.client.primary.addr6'
                    cmd = '%s "%s"' % (name, ntps_ip)
                    ntpc1.sendAndExpect(cmd, self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.backup.addr6', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.primary.addr', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.backup.addr', self.vxprompt)
                else:
                    name = 'sysvar set -co ipsntp.client.primary.addr'
                    cmd = '%s "%s"' % (name, ntps_ip)
                    ntpc1.sendAndExpect(cmd, self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.backup.addr', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.primary.addr6', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.backup.addr6', self.vxprompt)
                ntpc1.sendAndExpect('sysvar list ipsntp', self.vxprompt)
                ntpc1.sendAndExpect('ipd start ipsntp', self.vxprompt)
                # sleep for 20 seconds while time is updated
                time.sleep(20)
                ntpc1.send("date")
                ntpc1.expect(r"20[0-9][0-9]")
                ntpc1.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # set invalid time
                ntpc1.sendAndExpect("date 1999-01-02", "ok")
                ntpc1.sendAndExpect("date", "1999")
                # start sntp client daemon with secondary server
                if version == 'IPv6':
                    name = 'sysvar set -co ipsntp.client.backup.addr6'
                    cmd = '%s "%s"' % (name, ntps_ip)
                    ntpc1.sendAndExpect(cmd, self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.primary.addr6', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.primary.addr', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.backup.addr', self.vxprompt)
                else:
                    name = 'sysvar set -co ipsntp.client.backup.addr'
                    cmd = '%s "%s"' % (name, ntps_ip)
                    ntpc1.sendAndExpect(cmd, self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.primary.addr', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.primary.addr6', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.backup.addr6', self.vxprompt)
                ntpc1.sendAndExpect('sysvar list ipsntp', self.vxprompt)
                ntpc1.sendAndExpect('ipd start ipsntp', self.vxprompt)
                # sleep for 40 seconds while time is updated
                time.sleep(40)
                ntpc1.send("date")
                ntpc1.expect(r"20[0-9][0-9]")
                stop_ntpd(ntps, self.lxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_client_multicast(self, version):
        with allure.step('Test the SNTP multicast client'):
            """SNTP multicast client.
              This tests the SNTP multicast client.
              1. Set incorrect system time on target.
              2. Start Linux ntpd (multicast enabled).
              3. Use SNTP multicast client to wait for server multicast from Linux host.
              4. Verify that system time is updated on target.
              5. Redo 1-4 for ipv6"""
            ntpc1, ntps = self.t1, self.t_lx  # t s
            name = 'client_multicast'
            case_name = self.module + '.' + name + '-' + version

            try:
                if version == 'IPv6':
                    file_name = 'ntp.server.multicast.v6.conf'
                    ntpc1_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    file_name = 'ntp.server.multicast.v4.conf'
                    ntpc1_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                ntpc1.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                # set invalid time
                ntpc1.sendAndExpect("date 1999-01-02", "ok")
                ntpc1.sendAndExpect("date", "1999")
                # start sntp client daemon in multicast mode
                ntpc1.sendAndExpect('sysvar set -co ipsntp.client.poll.interval "0"', self.vxprompt)
                if version == 'IPv6':
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.multi.if6 "eth0"', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.multi.addr6', 'ff05::101')
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.multi.if', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.multi.addr', self.vxprompt)
                else:
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.multi.if"eth0"', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.multi.addr "224.0.1.1"', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.multi.if6', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.multi.addr6', self.vxprompt)
                ntpc1.sendAndExpect('sysvar list ipsntp', self.vxprompt)
                ntpc1.sendAndExpect('ipd start ipsntp', self.vxprompt)
                # sleep for 150 seconds while time is updated
                time.sleep(150)
                ntpc1.send("date")
                ntpc1.expect(r"20[0-9][0-9]")
                stop_ntpd(ntps, self.lxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_client_broadcast(self, version):
        with allure.step('Test the SNTP broadcast client'):
            """SNTP broadcast client.
            This tests the SNTP broadcast client.
            1. Set incorrect system time on target.
            2. Start Linux ntpd (broadcast enabled).
            3. Use SNTP broadcast client to wait for server broadcast from Linux host.
            4. Verify that system time is updated on target"""
            ntpc1, ntps = self.t1, self.t_lx  # t s
            name = 'client_multicast'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.broadcast.conf'

            try:
                if version == 'IPv6':
                    ntpc1_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc1_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                ntpc1.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                # cat ntp / ntp.server.broadcast.conf | sed "s:255.255.255.255:10.78.1.255:" > ntp / ntp.server.broadcast.conf.netbroadcast
                ntps.sendAndExpect('cat ~/ntp/%s | sed "s:255.255.255.255:%s:" > ~/ntp/%s.clientbroadcast' % (
                    file_name, "192.168.123.255", file_name), self.lxprompt)
                start_ntpd(ntps, file_name + ".clientbroadcast", self.lxprompt, ntps_ip)

                # set invalid time
                ntpc1.sendAndExpect("date 1999-01-02", "ok")
                ntpc1.sendAndExpect("date", "1999")
                # start sntp client daemon in multicast mode
                ntpc1.sendAndExpect('sysvar set -co ipsntp.client.poll.interval "0"', self.vxprompt)
                if version == 'IPv6':
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.multi.if6 "eth0"', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.multi.addr6', 'ff05::101')
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.multi.if', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.multi.addr', self.vxprompt)
                else:
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.multi.if "eth0"', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar set -co ipsntp.client.multi.addr "224.0.1.1"', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.multi.if6', self.vxprompt)
                    ntpc1.sendAndExpect('sysvar unset ipsntp.client.multi.addr6', self.vxprompt)
                ntpc1.sendAndExpect('sysvar list ipsntp', self.vxprompt)
                ntpc1.sendAndExpect('ipd start ipsntp', self.vxprompt)
                # sleep for 150 seconds while time is updated
                time.sleep(150)
                ntpc1.send("date")
                ntpc1.expect(r"20[0-9][0-9]")
                stop_ntpd(ntps, self.lxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_client_api_unicast(self, version):
        with allure.step('Test the SNTP unicast client API'):
            """SNTP unicast API
            This tests the SNTP unicast client API.
            1. Set incorrect system time on target.
            2. Start Linux ntpd (broadcast/multicast disabled).
            3. Use API to send sntp unicast message from target to Linux host.
            4. Verify that system time is updated on target.
            5. Redo 1-4 for ipv6"""
            ntpc1, ntpc2, ntps = self.t1, self.t2, self.t_lx  # t z s
            name = 'api_unicast'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.unicast.conf'
            try:
                if version == 'IPv6':
                    ntpc1_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc1_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                ntpc1.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                # set invalid time
                ntpc1.sendAndExpect("date 1999-01-02", "ok")
                ntpc1.sendAndExpect("date", "1999")
                ntpc1.send('sntp')
                ntpc1.expect("The sntp command will exit with 0 on success, and non-zero on errors.")
                # get new time
                ntpc1.send('sntp -t 20 -p 123 ' + ntps_ip)
                ntpc1.expect("System time updated")
                ntpc1.send("date")
                ntpc1.expect(r"20[0-9][0-9]")
                stop_ntpd(ntps, self.lxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_client_api_multicast(self, version):
        with allure.step('Test the SNTP multicast client API'):
            """SNTP multicast API.
            This tests the SNTP multicast client API.
            1. Set incorrect system time on target.
            2. Start Linux ntpd (multicast enabled).
            3. Use API to wait for server multicast from Linux host.
            4. Verify that system time is updated on target.
            5. Redo 1-4 for ipv6"""
            ntpc1, ntps = self.t1, self.t_lx  # t s
            name = 'api_multicast'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.unicast.conf'
            try:
                if version == 'IPv6':
                    file_name = 'ntp.server.multicast.v6.conf'
                    multicastaddr = 'ff05::101'
                    ntpc1_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    file_name = 'ntp.server.multicast.v4.conf'
                    multicastaddr = '224.0.1.1'
                    ntpc1_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                ntpc1.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                # set invalid time
                ntpc1.sendAndExpect("date 1999-01-02", "ok")
                ntpc1.sendAndExpect("date", "1999")
                # wait for new time
                ntpc1.send('sntp -t 100 -i ' + 'eth0' + ' ' + multicastaddr)
                ntpc1.expect("System time updated", timeout=120)
                ntpc1.send("date")
                ntpc1.expect(r"20[0-9][0-9]")
                stop_ntpd(ntps, self.lxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_sntp_client_api_broadcast(self, version):
        with allure.step('Test the SNTP broadcast client API'):
            """SNTP broadcast API.
            This tests the SNTP broadcast client API.
            1. Set incorrect system time on target.
            2. Start Linux ntpd (broadcast enabled).
            3. Use API to wait for server broadcast from Linux host.
            4. Verify that system time is updated on target"""

            ntpc1, ntps = self.t1, self.t_lx  # t s
            name = 'client_multicast'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.broadcast.conf'

            try:
                if version == 'IPv6':
                    ntpc1_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc1_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                ntpc1.sendAndExpect('ipd kill ipsntp', self.vxprompt)
                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                # cat ntp / ntp.server.broadcast.conf | sed "s:255.255.255.255:10.78.1.255:" > ntp / ntp.server.broadcast.conf.netbroadcast
                ntps.sendAndExpect('cat ~/ntp/%s | sed "s:255.255.255.255:%s:" > ~/ntp/%s.netbroadcast' % (
                    file_name, "192.168.123.255", file_name), self.lxprompt)
                start_ntpd(ntps, file_name + ".netbroadcast", self.lxprompt, ntps_ip)

                # set invalid time
                ntpc1.sendAndExpect("date 1999-01-02", "ok", timeout=300)
                ntpc1.send("date", "1999")
                # wait for new time
                ntpc1.send('sntp -t 150 -b')
                ntpc1.expect("System time updated", timeout=200)
                ntpc1.send("date")
                ntpc1.expect(r"20[0-9][0-9]")
                stop_ntpd(ntps, self.lxprompt)
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
