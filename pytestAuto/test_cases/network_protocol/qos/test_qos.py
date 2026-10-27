#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/28/2024 4:30 PM
@file:test_ntp.py
"""
import time
import allure
import pytest
import sys
import os
import re
from datetime import date, datetime, timedelta

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage


def basic(c, s, qarg, buflen, prompt, ip, eth_name):
    log.info("Set queue and args to %s" % qarg)

    def int2(c, s, buflen, prompt, ip):
        c.sendAndExpect('sysvar set -co ipcom.telnet.max_sessions "0"', prompt)
        s.sendAndExpect('sysvar set -co ipcom.telnet.max_sessions "0"', prompt)
        # Use some secondary shells, so that if they 'hang' in the test
        # the cleanup may still go through.

        # s2.ttcp_sink(v6=s.ip().v6, timeout=timeout) # xiaozhan, need to manual debug
        s.send('ttcp -r -p 5001 -b 16384')  # xiaozhan, modify

        # c2.ttcp_source(s.ip(), v6=c.ip().v6, buflen=buflen, nbuf=1024, timeout=timeout)
        # xiaozhan, modify
        cmd = f'ttcp -t -p 5001 -b 16384 -n 1024 -l {buflen} {ip}'
        c.send(cmd)
        # xiaozhan, modify
        s.expect(r'ttcp-[rt]: ([0-9]+) bytes in ([-0-9]+) milliseconds = ([0-9]+) KB/sec, ([0-9]+) B/msec', timeout=240)
        c.expect(r'ttcp-[rt]: ([0-9]+) bytes in ([-0-9]+) milliseconds = ([0-9]+) KB/sec, ([0-9]+) B/msec', timeout=240)


    # RTO recovers much faster if the timestamp option is enabled
    # c_shell.configure_tcp_timestamp(True)
    # xiaozhan, modify
    c.sendAndExpect('sysvar set -co iptcp.opt.Timestamp "1"', prompt)
    s.sendAndExpect('sysvar set -co iptcp.opt.Timestamp "1"', prompt)
    # qc add queue, xiaozhan, modify
    c.sendAndExpect('qc queue add dev %s %s' % (eth_name, qarg), prompt)
    s.sendAndExpect('qc queue add dev %s %s' % (eth_name, qarg), prompt)
    # c.netif().qc_add_queue(qarg)

    int2(c, s, buflen, prompt, ip)

    # if localhost:
    #     # c.netif(linktype='loopback').qc_add_queue(qarg)
    #     c.sendAndExpect('qc queue add dev lo0 %s' % qarg, prompt)
    #     int2(c, c, buflen, prompt, lo_ip)    # xiaozhan, chang ip to self.t1_ip instead of self.t2_ip


def basic_udp(c, s, qarg, buflen, checkrate, prompt, ip, localhost=False):
    log.info("Set queue and args to %s" % qarg)

    def int2(c, s, checkrate, prompt, ip):
        c.sendAndExpect('sysvar set -co ipcom.telnet.max_sessions "0"', prompt)
        s.sendAndExpect('sysvar set -co ipcom.telnet.max_sessions "0"', prompt)
        # Use some secondary shells, so that if they 'hang' in the test
        # the cleanup may still go through.

        timeout = 240

        s2.ttcp_sink(v6=s.ip().v6, timeout=timeout, udp=True)



        c2.ttcp_source(s.ip(), v6=c.ip().v6, buflen=buflen, nbuf=256, timeout=timeout, udp=True)
        s2.ttcp_expect(timeout=timeout)
        res = c2.ttcp_expect(timeout=timeout)
        # res[2] is KB/sec in ttcp_expect()
        if int(res[2], 10) > checkrate:
            log.error('Really rate %s must be less than setting rate:%d ' % (res[2], checkrate))
            assert False

    c_shell = c.ipcom_shell()
    s_shell = s.ipcom_shell()

    c.netif().qc_add_queue(qarg)
    s.netif().qc_add_queue(qarg)

    int2(c, s, checkrate)


def check_default_id(c, default_id, prompt):
    lines = c.sendAndReturnAll('qc queue show dev eth0', prompt)
    for i in range(len(lines)):
        if lines[i].strip() and lines[i].find('default id: %s' % default_id) != -1:
            return
    else:
        log.error('Can tot find any default id')
        assert False


class TestQOS(object):
    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-qos/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'qos.qos'
        self.lxprompt = r'ubuntu@ubuntu:~\$ '  # xiaozhan, must has \$
        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 3)]
        [x.boot(vximage) for x in self.vx_targets]

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

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_dpaf(self, version):
        with allure.step('Test drop presence-aware-FIFO (DPAF) queue'):
            c, s = self.t1, self.t2
            name = 'dpaf'
            case_name = self.module + '.' + name + '-' + version
            qarg = "dpaf limit 10"
            try:
                if version == 'IPv6':
                    ip = self.t2_ip6
                    lo_ip = self.t1_ip6
                else:
                    ip = self.t2_ip
                    lo_ip = self.t1_ip
                basic(c, s, qarg, 1000, self.vxprompt, ip, 'eth0')
                basic(c, c, qarg, 1000, self.vxprompt, lo_ip, 'lo0')
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_htbc(self, version):
        with allure.step('Test sending traffic without any queue attached to the interface'):
            c, s = self.t1, self.t2
            name = 'htbc'
            case_name = self.module + '.' + name + '-' + version
            try:
                if version == 'IPv6':
                    ip = self.t2_ip6
                    lo_ip = self.t1_ip6
                else:
                    ip = self.t2_ip
                    lo_ip = self.t1_ip

                basic(c, s, "htbc rate 100kbps burst 50kB", 700, self.vxprompt, ip, 'eth0')
                basic(c, s, "htbc rate 100kbps burst 50kB", 700, self.vxprompt, lo_ip, 'lo0')

            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_htbc_default(self, version):
        with allure.step('Test to change default queue when using Hierarchical Token Bucket Container (HTBC)'):
            c = self.t1
            name = 'htbc_default'
            case_name = self.module + '.' + name + '-' + version
            try:
                c.sendAndExpect("qc queue add dev eth0 root handle 1 mbc bands 2 default_band 0", self.vxprompt)
                c.sendAndExpect("qc queue add dev eth0 parent 1 handle 1000 htbc rate 70kbps", self.vxprompt)
                check_default_id(c, '1002', self.vxprompt)
                c.sendAndExpect("qc queue add dev eth0 parent 1000 handle 2001 htbc rate 20kbps default", self.vxprompt)
                check_default_id(c, '2001', self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_mbc(self, version):
        with allure.step('Test sorting of traffic flows into different behaviors using Multi Band Container (MBC)'):
            c, s = self.t1, self.t2
            name = 'mbc'
            case_name = self.module + '.' + name + '-' + version

            def internal(c, s, qarg, prompt, ip, eth_name, cmd):
                s.sendAndExpect('qc queue add dev %s handle 1 %s' % (eth_name, qarg), prompt)
                s.sendAndExpect('qc queue add dev %s parent 1 handle 1000 null' % eth_name, prompt)
                s.sendAndExpect('qc filter add dev %s parent 1 handle 1 proto 1 flowid 1000' % eth_name, prompt)

                log("The ping should fail since all ICMP traffic is now dropped")
                ret = '\n'.join(c.sendAndReturnAll(cmd, prompt))
                assert '100% packet loss' in ret

                s.sendAndExpect('qc filter del dev %s parent 1 handle 1' % eth_name, prompt)
                basic(c, s, qarg, 1000, prompt, ip, eth_name)
            try:
                qarg = "mbc bands 2"
                eth_name = 'eth0'
                if version == 'IPv6':
                    ip = self.t2_ip6
                    cmd = f'ping6 -c 2 %s' % ip
                else:
                    ip = self.t2_ip
                    cmd = f'ping -c 2 %s' % ip
                internal(c, s, qarg, self.vxprompt, ip, eth_name, cmd)
                # xiaozhan, add
                eth_name = 'lo0'
                if version == 'IPv6':
                    ip = self.t1_ip6
                    cmd = f'ping6 -c 2 %s' % ip
                else:
                    ip = self.t1_ip
                    cmd = f'ping -c 2 %s' % ip
                internal(c, c, qarg, self.vxprompt, ip, eth_name, cmd)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_netemu(self, version):
        """Test sending traffic trough the NETMU queue which will simulate a link
            - where packets experience random latency and reordering
            - where some packets are dropped
            - where some packet get corrupted during transit"""
        with allure.step('Test sending traffic trough the NETMU queue'):
            c, s = self.t1, self.t2
            name = 'netemu'
            case_name = self.module + '.' + name + '-' + version
            try:
                if version == 'IPv6':
                    ip = self.t2_ip6
                    lo_ip = self.t1_ip6
                else:
                    ip = self.t2_ip
                    lo_ip = self.t1_ip

                basic(c, s, "netemu limit 60 min_latency 20 max_latency 40", 50, self.vxprompt, ip, 'eth0')
                basic(c, s, "netemu limit 60 min_latency 20 max_latency 40", 50, self.vxprompt, lo_ip, 'lo0')
                basic(c, s, "netemu limit 10 drop 60", 100, self.vxprompt, ip, 'eth0')
                basic(c, s, "netemu limit 10 drop 60", 100, self.vxprompt, lo_ip, 'lo0')

                basic(c, s, "netemu limit 10 corrupt 50 random", 75, self.vxprompt, ip, 'eth0')
                basic(c, s, "netemu limit 60 drop 20 pattern 8", 60, self.vxprompt, ip, 'eth0')
                basic(c, s, "netemu limit 60 drop 20 random", 60, self.vxprompt, ip, 'eth0')
                basic(c, s, "netemu limit 60 drop 20 corrupt 50 random", 60, self.vxprompt, ip, 'eth0')
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_none(self, version):
        with allure.step('Test sending traffic without any queue attached to the interface'):
            c, s = self.t1, self.t2
            name = 'none'
            case_name = self.module + '.' + name + '-' + version
            try:
                if version == 'IPv6':
                    ip = self.t2_ip6
                    lo_ip = self.t1_ip6
                else:
                    ip = self.t2_ip
                    lo_ip = self.t1_ip

                basic(c, s, "none", 1000, self.vxprompt, ip, 'eth0')
                basic(c, s, "none", 1000, self.vxprompt, lo_ip, 'lo0')

            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_block_on_netif(self, version):
        with allure.step('Test that a process sending on a blocking socket can block on the outgoing interface'):
            c, s = self.t1, self.t2
            name = 'block_on_netif'
            case_name = self.module + '.' + name + '-' + version
            try:
                if version == 'IPv6':
                    ip = self.t2_ip6
                    lo_ip = self.t1_ip6
                else:
                    ip = self.t2_ip
                    lo_ip = self.t1_ip

                # old
                c.sendAndExpect('qc queue add dev eth0 netemu limit 4 min_latency 20 max_latency 50', self.vxprompt)
                # xiaozhan, debug, too complicated
                c.try_flood(s, 10, s.netif().ip(v6), v6)

            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_hierarchy(self, version):
        with allure.step('Configure and run traffic through a hierarchy of queues'):
            c, s = self.t1, self.t2
            name = 'hierarchy'
            case_name = self.module + '.' + name + '-' + version
            try:
                if version == 'IPv6':
                    ip = self.t2_ip6
                    lo_ip = self.t1_ip6
                else:
                    ip = self.t2_ip
                    lo_ip = self.t1_ip

                # Add verification of defect WIND00140644
                c.sendAndExpect('qc queue add dev eth0 root handle 10 mbc bands 2 default_band 1', self.vxprompt)
                c.sendAndExpect('qc queue add dev eth0 parent 10 handle 1000 htbc rate 15Mbit burst 64kB', self.vxprompt)
                # This line will cause a kernel panic if defect WIND00140644
                # is present
                c.sendAndExpect('qc queue add dev eth0 parent 1000 handle 1002 fifo limit 100', self.vxprompt)
                # TODO xiaozhan   debug
                c.try_flood(s, 3, peer.netif().ip(v6), v6)

            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_invalid_config(self, version):
        with allure.step('Pass a number of invalid configurations to the qc command'):
            c, = self.t1
            name = 'invalid_config'
            case_name = self.module + '.' + name + '-' + version
            try:
                # TODO xiaozhan  debug
                # Add verification of defect WIND00140644
                c.sendAndExpect('qc queue add dev eth0 root handle 10 mbc bands 2 default_band 1', self.vxprompt)
                # This line will cause a kernel panic if defect WIND00140644
                # is present
                c.sendAndExpect('qc queue add dev eth0 parent 10 handle 11 htbc rate 15Mbit burst 64kB', self.vxprompt)

                for cmd in ['root handle 10 mbc bandsXX 2 default_band 1',
                            'root htbc rate 15millibit burst 100kB',
                            'root fifo limit -10',
                            'root non_existing_type a 1']:
                    c.sendAndExpect(cmd, self.vxprompt)
                # TODO debug  xiaozhan
                # Following must fail since ID=1 is reused by a child
                c.sendAndExpect('qc queue add dev eth0 root handle 1 htbc rate 2Mbit', self.vxprompt)
                c.sendAndExpect('qc queue add dev eth0 parent 1 handle 3 htbc rate 2Mbit', self.vxprompt)
                netif.qc_add_queue('parent 3 handle 1 mbc bands 2', succeed=False)

                # The following lines will cause a kernel panic if defect
                # WIND00179681 is present (using the same ID twice)
                netif.qc_add_queue('root handle 1 htbc rate 2Mbit')
                netif.qc_add_queue('parent 1 handle 1 mbc bands 2', succeed=False)

                # The following lines will cause a kernel panic if defect
                # WIND00179681 is present (replacing a non-existing MBC band
                # with another MBC)
                netif.qc_add_queue('root handle 1 htbc rate 2Mbit')
                netif.qc_add_queue('parent 1 handle 3 mbc bands 2')
                netif.qc_add_queue('parent 3 handle 5 mbc bands 2', succeed=False)

    def teardown_class(self):
        # clean up vxworks
        for t in self.vx_targets:
            t.cleanup()
            t.logFile.close()
        # process self.result ----store result,upload to Database or sth like that
        for i in self.result:
            if i[1] == 'PASS':
                self.pass_num += 1
            else:
                self.fail_num += 1
        log.info(self.result)
        log.info(f'total:{len(self.result)}, pass:{self.pass_num}, fail:{self.fail_num}')
