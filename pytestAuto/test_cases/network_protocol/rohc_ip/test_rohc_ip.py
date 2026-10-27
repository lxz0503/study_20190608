#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:5/4/2024 4:30 PM
@file:test_rohc_ip.py
"""
import time
import allure
import pytest
import sys
import os
import re
from datetime import date, datetime, timedelta

from pytestAuto.utils.iprohc_common import RohcBase, config_pppoe, pppoe_addr

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage
from utils.iprohc_common import *
from utils.ipcom_session import echo_server, echo_client, stop_echoserver
from tunnel import _test_setup, _test_tunnel, _has_ipv6_support


class TestRohcIP(object):
    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-rohc-ip/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'iprohc_ip.iprohc_ip'
        self.lxprompt = r'ubuntu@ubuntu:~\$ '  # xiaozhan, must has \$
        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 4)]
        [x.boot(vximage) for x in self.vx_targets]

        lximage = LinuxImage('/home/xli3/pytestAuto/config/focal-server-cloudimg-amd64.img')
        self.t_lx = QemuTarget('QEMU-LX-1', logFile='linuxqemu.log')
        self.t_lx.boot(lximage)

        # qemu VxWorks
        self.t1, self.t2, self.t3 = self.vx_targets
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::10 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.10 prefixlen 24 up', self.vxprompt)

        self.t2.sendAndExpect('cmd', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet6 add 2000::20 prefixlen 64 up', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet add 10.236.1.20 prefixlen 24 up', self.vxprompt)

        self.t3.sendAndExpect('cmd', self.vxprompt)
        self.t3.sendAndExpect('ifconfig eth0 inet6 add 2000::30 prefixlen 64 up', self.vxprompt)
        self.t3.sendAndExpect('ifconfig eth0 inet add 10.236.1.30 prefixlen 24 up', self.vxprompt)

        self.t1_ip, self.t1_ip6 = self.t1.get_ip()
        self.t2_ip, self.t2_ip6 = self.t2.get_ip()
        self.t3_ip, self.t3_ip6 = self.t3.get_ip()

        self.lx_ip, self.lx_ip6 = self.t_lx.get_ip()

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_small_cid(self, version):
        with allure.step('Test IP profile with small CID'):
            dut1, dut2 = self.t1, self.t2  # xiaozhan, c s p  --3 targets
            name = 'small_cid'
            case_name = self.module + '.' + name + '-' + version

            try:
                peer1 = RohcBase(dut1)
                peer2 = RohcBase(dut2)

                # Small CID, xiaozhan
                dut1.sendAndExpect('sysvar set -co iprohc.large_cid "0"', self.vxprompt)
                dut2.sendAndExpect('sysvar set -co iprohc.large_cid "0"', self.vxprompt)

                # Configure PPPoE --- c s p - 3 targets
                addr1, addr2, if_name1, if_name2 = config_pppoe(self.vx_targets, peer1, peer2, self.vxprompt, version)

                # Prepare PPPoE addresses for use----- c s p -- 3 targets
                addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, version)

                # Configure ROHC
                peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '4', '1')
                peer1.rohc_shell_exit()
                peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '4', '1')
                peer2.rohc_shell_exit()

                # Begin testing
                # Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
                # Between ports 7302/7301 in both directions
                echo_server(dut1, addr1_s, proto='udp')
                echo_server(dut2, addr2_s, proto='udp')
                echo_client(dut1, addr2_c, proto='udp', nbuf=100, chunk_size=1, local_port=7302, verify_data=True)
                echo_client(dut2, addr1_c, proto='udp', nbuf=100, chunk_size=1, local_port=7302, verify_data=True)

                # Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
                # Between ports 7302/7301 in both directions
                echo_client(dut1, addr2_c, proto='udp', nbuf=100, chunk_size=100, local_port=7302, verify_data=True)
                echo_client(dut2, addr1_c, proto='udp', nbuf=100, chunk_size=100, local_port=7302, verify_data=True)

                # Search for failed decompression
                peer1.lookup_for_failed_decompression()
                peer2.lookup_for_failed_decompression()

                stop_echoserver(dut1)
                stop_echoserver(dut2)

                # Clean up the ROHC
                peer1.rohc_shell_start()
                peer1.rohc_close()
                peer1.rohc_shell_exit()
                peer2.rohc_shell_start()
                peer2.rohc_close()
                peer2.rohc_shell_exit()

                stop_echoserver(dut1)
                stop_echoserver(dut2)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_large_cid(self, version):
        with allure.step('Test IP profile with large CID'):
            dut1, dut2 = self.t1, self.t2  # xiaozhan, c s p  --3 targets
            name = 'large_cid'
            case_name = self.module + '.' + name + '-' + version

            try:
                peer1 = RohcBase(dut1)
                peer2 = RohcBase(dut2)

                # Configure PPPoE
                addr1, addr2, if_name1, if_name2 = config_pppoe(self.vx_targets, peer1, peer2, version)

                # Prepare PPPoE addresses for use
                addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, version)

                # Large CID
                dut1.sendAndExpect('sysvar set -co iprohc.large_cid "1"', self.vxprompt)
                dut1.sendAndExpect('sysvar set -co iprohc.max_cid "5000"', self.vxprompt)
                dut2.sendAndExpect('sysvar set -co iprohc.large_cid "1"', self.vxprompt)
                dut2.sendAndExpect('sysvar set -co iprohc.max_cid "5000"', self.vxprompt)

                # Configure ROHC 
                peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '4', '2000')
                peer1.rohc_shell_exit()
                peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '4', '2000')
                peer2.rohc_shell_exit()

                # Begin testing
                echo_server(dut1, addr1_s, proto='udp')
                echo_server(dut2, addr2_s, proto='udp')

                # Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
                # Between ports 7302/7301 in both directions
                echo_server(dut1, addr2_c, proto='udp', nbuf=100, chunk_size=1, local_port=7302, verify_data=True)
                echo_server(dut2, addr1_c, proto='udp', nbuf=100, chunk_size=1, local_port=7302, verify_data=True)

                # Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
                # Between ports 7302/7301 in both directions
                echo_server(dut1, addr2_c, proto='udp', nbuf=100, chunk_size=100, local_port=7302, verify_data=True)
                echo_server(dut2, addr1_c, proto='udp', nbuf=100, chunk_size=100, local_port=7302, verify_data=True)
                echo_server(dut1, addr2_c, proto='udp', nbuf=200, chunk_size=100, local_port=7302, verify_data=True)
                echo_server(dut2, addr1_c, proto='udp', nbuf=200, chunk_size=100, local_port=7302, verify_data=True)

                # Search for failed decompression
                peer1.lookup_for_failed_decompression()
                peer2.lookup_for_failed_decompression()

                # Clean up the ROHC
                peer1.rohc_shell_start()
                peer1.rohc_close()
                peer1.rohc_shell_exit()
                peer2.rohc_shell_start()
                peer2.rohc_close()
                peer2.rohc_shell_exit()

                # Clean up 
                stop_echoserver(dut1)
                stop_echoserver(dut2)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_large_cid_small_val(self, version):
        with allure.step('Test IP profile with large CID and small value'):
            dut1, dut2 = self.t1, self.t2  # xiaozhan, c s p  --3 targets
            name = 'large_cid_small_val'
            case_name = self.module + '.' + name + '-' + version

            try:
                peer1 = RohcBase(dut1)
                peer2 = RohcBase(dut2)

                dut1.sendAndExpect('sysvar set -co iprohc.large_cid "1"', self.vxprompt)
                dut2.sendAndExpect('sysvar set -co iprohc.large_cid "1"', self.vxprompt)
                dut1.sendAndExpect('sysvar set -co iprohc.max_cid "50"', self.vxprompt)
                dut2.sendAndExpect('sysvar set -co iprohc.max_cid "50"', self.vxprompt)

                # Configure PPPoE
                addr1, addr2, if_name1, if_name2 = config_pppoe(self.vx_targets, peer1, peer2, version)

                # Prepare PPPoE addresses for use
                addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, version)

                # Configure ROHC
                peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '4', '2')
                peer1.rohc_shell_exit()
                peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '4', '2')
                peer2.rohc_shell_exit()

                # Begin testing
                echo_server(dut1, addr1_s, proto='udp')
                echo_server(dut2, addr2_s, proto='udp')

                # Test a connection for packets shorter 64(IPv4) and 50(IPv6) bytes
                # Between ports 7302/7301 in both directions
                echo_client(dut1, addr2_c, proto='udp', nbuf=100, chunk_size=1, local_port=7302, verify_data=True)
                echo_client(dut2, addr1_c, proto='udp', nbuf=100, chunk_size=1, local_port=7302, verify_data=True)

                # Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
                # Between ports 7302/7301 in both directions
                echo_client(dut1, addr2_c, proto='udp', nbuf=100, chunk_size=100, local_port=7302, verify_data=True)
                echo_client(dut2, addr1_c, proto='udp', nbuf=100, chunk_size=100, local_port=7302, verify_data=True)
                echo_client(dut1, addr2_c, proto='udp', nbuf=200, chunk_size=100, local_port=7302, verify_data=True)
                echo_client(dut2, addr1_c, proto='udp', nbuf=200, chunk_size=100, local_port=7302, verify_data=True)

                # Search for failed decompression
                peer1.lookup_for_failed_decompression()
                peer2.lookup_for_failed_decompression()

                # Clean up the ROHC
                peer1.rohc_shell_start()
                peer1.rohc_close()
                peer1.rohc_shell_exit()
                peer2.rohc_shell_start()
                peer2.rohc_close()
                peer2.rohc_shell_exit()

                # Clean up
                stop_echoserver(dut1)
                stop_echoserver(dut2)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_mine_enc_pppoe(self, version):
        with allure.step('ROHC IP: Mine encapsulation test (GRE)'):
            dut1, dut2, dut3 = self.t1, self.t2, self.t3  # xiaozhan, c s p  --3 targets
            name = 'mine_enc_pppoe'
            case_name = self.module + '.' + name + '-' + version

            def wait_tcp_ready(host, timeout=80):
                # wait tcp ready or S_errno_EADDRINUSE happens
                start_time = time.time()
                i = 0

                while True:
                    if (time.time() - start_time) >= timeout:
                        print('=== wait_tcp_ ready() timeout after %s seconds' % timeout)
                        break

                    lines = host.shops.send_and_return_all("netstat -P")
                    if '\n'.join(lines).find('TIME_WAIT') != -1:
                        time.sleep(1)
                        i += 1
                    else:
                        break

            try:

                # Configure PPPoE and ROHC
                addr1_c, addr2_c, addr1_s, addr2_s = config_pppoe_rohc(hosts, version, 4)
                addr1, addr2, tunnel_ifs = test_setup(log, "min", dut1, dut2, addr1_c, addr2_c, 17, version)

                # Begin testing
                echo_server(dut1, addr1, proto='tcp')
                echo_server(dut2, addr2, proto='tcp')

                # Test a connection for short packets
                # Between ports 7302/7301 in both directions
                echo_client(dut1, addr2, proto='tcp', nbuf=1, chunk_size=100, local_port=7302, verify_data=True,
                            reuse_addr=True)
                echo_client(dut1, addr1, proto='tcp', nbuf=100, chunk_size=1, local_port=7302, verify_data=True,
                            reuse_addr=True)

                # Test a connection for packets longer 64(IPv4) and 50(IPv6) bytes
                # Between ports 7302/7301 in both directions
                wait_tcp_ready(dut1)
                echo_client(dut1, addr2, proto='tcp', nbuf=100, chunk_size=1100, local_port=7302, verify_data=True,
                            reuse_addr=True)
                echo_client(dut1, addr1, proto='tcp', nbuf=100, chunk_size=1100, local_port=7302, verify_data=True,
                            reuse_addr=True)

                # Test 2 connections with the same destination port
                echo_client(dut1, addr2, proto='tcp', nbuf=20, chunk_size=1100, local_port=7304, verify_data=True,
                            reuse_addr=True)
                echo_client(dut1, addr2, proto='tcp', nbuf=20, chunk_size=1100, local_port=7305, verify_data=True,
                            reuse_addr=True)
                echo_client(dut1, addr1, proto='tcp', nbuf=20, chunk_size=1100, local_port=7304, verify_data=True,
                            reuse_addr=True)
                echo_client(dut1, addr1, proto='tcp', nbuf=20, chunk_size=1100, local_port=7305, verify_data=True,
                            reuse_addr=True)

                # Test 2 connections with the same source ports
                # Between ports 7302/7301 in both directions
                wait_tcp_ready(dut1)
                echo_client(dut1, addr2, proto='tcp', nbuf=20, chunk_size=1100, local_port=7304, verify_data=True,
                            reuse_addr=True)
                wait_tcp_ready(dut2)
                echo_client(dut1, addr1, proto='tcp', nbuf=20, chunk_size=1100, local_port=7304, verify_data=True,
                            reuse_addr=True)
                dut1.stop_echoserver()
                dut2.stop_echoserver()
                echo_server(dut1, addr1, proto='tcp', port=7307)
                echo_server(dut2, addr2, proto='tcp', port=7307)
                echo_client(dut1, addr2, proto='tcp', nbuf=20, chunk_size=1100, local_port=7304, port=7307,
                            verify_data=True, reuse_addr=True)
                echo_client(dut1, addr1, proto='tcp', nbuf=20, chunk_size=1100, local_port=7304, port=7307,
                            verify_data=True, reuse_addr=True)

                # Validate and celan up ROHC
                validate_and_cleanup_rohc(self.vx_targets)

                stop_echoserver(dut1)
                stop_echoserver(dut2)

                for t in tunnel_ifs:
                    t.destroy()

                return
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
