#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 10/31/2022 12:49 PM
# @Email = lxz_20081025@163.com
# @Name = xiaozhan_test_1.py
import allure
import pytest
import sys
sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.vlmTarget import boot_target_28610
from utils.parser_iperf import parser_iperf


class TestSuite28610(object):
    def setup_class(self):
        self.tgt = boot_target_28610()
        self.tgt.sendAndExpect('ipAttach 0,"gei"', 'value = 0 = 0x0', timeout=60)
        self.tgt.sendAndExpect('ifconfig "gei0 192.168.10.3/24 up"', 'value = 0 = 0x0', timeout=60)
        self.tst_dict = {}

    def teardown_class(self):
        self.tgt.connClose()

    @allure.title('tcp 64 bytes payload')
    def test_tcp_64(self):
        Tx = True
        with allure.step('Payload is 64 bytes'):
            rets = self.tgt.sendAndReturnAll('sp iperf3,"-c 192.168.10.1 -t 20 -p 10000 -i 20 -l 64 -f m"',
                                             'iperf Done', timeout=25)
            rets = list(rets)
            tcp_64 = parser_iperf(rets, Tx)
        # store test result
        self.tst_dict['tcp_64'] = tcp_64
        # assert result
        with allure.step(f'assert {tcp_64} versus baseline 70 Mbits/sec'):
            assert 70 / int(tcp_64) <= 1.1

    @allure.title('tcp 1024 bytes payload')
    def test_tcp_1024(self):
        Tx = True
        with allure.step('Payload is 1024 bytes'):
            rets = self.tgt.sendAndReturnAll('sp iperf3,"-c 192.168.10.1 -t 20 -p 10000 -i 20 -l 1024 -f m"',
                                             'iperf Done',
                                             timeout=25)
            rets = list(rets)
            tcp_1024 = parser_iperf(rets, Tx)
        # store test result
        self.tst_dict['tcp_1024'] = tcp_1024
        # assert result
        with allure.step(f'assert {tcp_1024} versus baseline 500 Mbits/sec'):
            assert 500 / int(tcp_1024) <= 1.1

    @allure.title('tcp 65536 bytes payload')
    def test_tcp_65536(self):
        Tx = True
        with allure.step('Payload is 65536 bytes'):
            rets = self.tgt.sendAndReturnAll('sp iperf3,"-c 192.168.10.1 -t 20 -p 10000 -i 20 -l 65536 -f m"',
                                             'iperf Done', timeout=25)
            rets = list(rets)
            tcp_65536 = parser_iperf(rets, Tx)
        # store test result
        self.tst_dict['tcp_65536'] = tcp_65536
        # assert result
        with allure.step(f'assert {tcp_65536} versus baseline 800 Mbits/sec'):
            assert 800 / int(tcp_65536) <= 1.1

    @allure.title('udp 1400 bytes payload')
    def test_udp_1400(self):
        Tx = True
        with allure.step('Payload is UDP 1400 bytes'):
            rets = self.tgt.sendAndReturnAll('sp iperf3,"-c 192.168.10.1 -t 20 -p 10000 -i 20 -l 1400 -f m -b 0 -u"',
                                             'iperf Done', timeout=25)
            rets = list(rets)
            #print('xiaozhan--debug--rets:', rets)
            udp_1400 = parser_iperf(rets, Tx)
        # store test result.
        self.tst_dict['udp_1400'] = udp_1400
        # assert result
        with allure.step(f'assert {udp_1400} versus baseline 955 Mbits/sec'):
            assert 955 / int(udp_1400) <= 1.1

