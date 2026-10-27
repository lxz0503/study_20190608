#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 3/27/2023 4:45 PM
# @Email = lxz_20081025@163.com
# @Name = XL710.py
import time
import datetime
import pandas as pd
from vlmTarget_IPERF_Trial import boot_target_916620
from parser_iperf import parser_iperf
from hm_21_paramiko_class_ssh import client_cmd_29076


class Test40G(object):
    tst_dict = {}  # This is class attribute storing test result

    def __int__(self):
        self.tgt4 = None
        self.cmd_input = ""

    def config_tgt(self):
        self.tgt4 = boot_target_916620()  # boot target 916620
        self.tgt4.sendAndExpect('ipAttach 0,"qei"', 'value = 0 = 0x0', timeout=10)
        self.tgt4.sendAndExpect('ifconfig "qei0 10.0.0.1/24 up"', 'value = 0 = 0x0', timeout=10)
        self.tgt4.sendAndExpect('cmd ethtool -K qei0 lro on', '->', timeout=10)

    def start_iperf(self):
        # start IPERF
        self.cmd_input = 'pkill iperf3'
        client_cmd_29076.run_ssh(self.cmd_input)
        self.cmd_input = 'iperf3 -s -p 10000 -1 &'
        client_cmd_29076.run_ssh(self.cmd_input)

    def close_tgt(self):
        # close telnet session
        self.tgt4.connClose()

    def close_iperf(self):
        # close iperf process
        self.cmd_input = 'pkill iperf3'
        client_cmd_29076.run_ssh(self.cmd_input)

    def test_tcp_64(self):
        self.start_iperf()
        Tx = True
        print('Payload is 64 bytes')
        rets = self.tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -N -t 20 -p 10000 -i 20 -l 64 -f m -P 1"',
                                          'iperf Done',
                                          timeout=25)
        rets = list(rets)
        tcp_64 = parser_iperf(rets, Tx)
        print(f'assert {tcp_64} versus baseline 313 Mbits/sec')
        if 313 / int(tcp_64) >= 1.1:
            print(f'tcp_64 result {tcp_64} is not ok')
        self.tst_dict['tcp_64'] = tcp_64
        # close iperf
        self.close_iperf()

    def test_tcp_1024(self):
        self.start_iperf()
        Tx = True
        rets = self.tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 1024 -f m -P 1"',
                                          'iperf Done',
                                          timeout=25)
        rets = list(rets)
        tcp_1024 = parser_iperf(rets, Tx)
        self.tst_dict['tcp_1024'] = tcp_1024
        # close iperf
        self.close_iperf()

    def test_tcp_65536(self):
        self.start_iperf()
        Tx = True
        print('===========Payload is 65536 bytes=============')
        rets = self.tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 65536 -f m -O 6 -w 2m"',
                                          'iperf Done',
                                          timeout=30)
        rets = list(rets)
        tcp_65536 = parser_iperf(rets, Tx)
        print(f'assert {tcp_65536} versus baseline 29300 Mbits/sec')
        if 29300 / int(tcp_65536) >= 1.1:
            print(f'tcp_65536 result {tcp_65536} is not ok')
        self.tst_dict['tcp_65536'] = tcp_65536
        # close iperf
        self.close_iperf()

    def test_udp_1400(self):
        self.start_iperf()
        Tx = True
        print('===========Payload is UDP 1400 bytes=============')
        rets = self.tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 1400 -f m -b 0 -u"',
                                          'iperf Done',
                                          timeout=30)
        rets = list(rets)
        udp_1400 = parser_iperf(rets, Tx)
        print(f'assert {udp_1400} versus baseline 10352 Mbits/sec')
        if 10352 / int(udp_1400) >= 1.1:
            print(f'udp_1400 result {udp_1400} is not ok')
        self.tst_dict['udp_1400'] = udp_1400
        # close iperf
        self.close_iperf()

    def test_tcp_rx_64(self):
        self.start_iperf()
        print('==============Below is for Rx test=============\n')
        Tx = False
        print('===========Payload is 64 bytes Rx==============')
        rets = self.tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -N -t 20 -p 10000 -i 20 -l 64 -f m -R"', 'iperf Done',
                                          timeout=25)
        rets = list(rets)
        tcp_64_Rx = parser_iperf(rets, Tx)
        print(f'assert {tcp_64_Rx} versus baseline 398 Mbits/sec')
        if 398 / int(tcp_64_Rx) >= 1.1:
            print(f'tcp_64_Rx result {tcp_64_Rx} is not ok')
        self.tst_dict['tcp_64_Rx'] = tcp_64_Rx
        # close iperf
        self.close_iperf()

    def test_tcp_rx_1024(self):
        self.start_iperf()
        Tx = False
        print('===========Payload is 1024 bytes  Rx=============')
        rets = self.tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 1024 -f m -R"', 'iperf Done',
                                          timeout=25)
        rets = list(rets)
        tcp_1024_Rx = parser_iperf(rets, Tx)
        print(f'assert {tcp_1024_Rx} versus baseline 4310 Mbits/sec')
        if 4310 / int(tcp_1024_Rx) >= 1.1:
            print(f'tcp_1024_Rx result {tcp_1024_Rx} is not ok')
        self.tst_dict['tcp_1024_Rx'] = tcp_1024_Rx
        # close iperf
        self.close_iperf()

    def test_tcp_rx_65536(self):
        self.start_iperf()
        Tx = False
        print('===========Payload is 65536 bytes Rx=============')
        rets = self.tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 65536 -f m -R"', 'iperf Done',
                                          timeout=30)
        rets = list(rets)
        tcp_65536_Rx = parser_iperf(rets, Tx)
        print(f'assert {tcp_65536_Rx} versus baseline 16828 Mbits/sec')
        if 16828 / int(tcp_65536_Rx) >= 1.1:
            print(f'tcp_65536_Rx result {tcp_65536_Rx} is not ok')
        self.tst_dict['tcp_65536_Rx'] = tcp_65536_Rx
        # close iperf
        self.close_iperf()

    def test_udp_rx_1400(self):
        self.start_iperf()
        Tx = False
        print('===========Payload is UDP 1400 bytes  Rx=============')
        rets = self.tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 1400 -f m -b 0 -u -R"',
                                          'iperf Done',
                                          timeout=30)
        rets = list(rets)
        udp_1400_Rx = parser_iperf(rets, Tx)
        print(f'assert {udp_1400_Rx} versus baseline 4420 Mbits/sec')
        if 4420 / int(udp_1400_Rx) >= 1.1:
            print(f'udp_1400_Rx result {udp_1400_Rx} is not ok')
        self.tst_dict['udp_1400_Rx'] = udp_1400_Rx
        # close iperf
        self.close_iperf()

    def process_iperf_result(self):
        # process test result
        for k in self.tst_dict:
            print("%s - %s" % (k, self.tst_dict[k]))
        # date_range = pd.date_range(start=time.strftime("%Y-%m-%d"), periods=1)
        # add below two lines   python3 /home/wrsadmin/tsn01/utils/trial_40G.py
        # Crontab job in the next morning, so modify the datetime to yesterday.
        yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).date().strftime('%Y-%m-%d')
        date_range = pd.date_range(start=yesterday, periods=1)
        df = pd.DataFrame(self.tst_dict, index=date_range)
        res_csv = '/home/wrsadmin/tsn01/csv_result_40G/' + yesterday + '.csv'
        df.to_csv(res_csv)

