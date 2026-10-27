#!/usr/bin/env python3
# encoding=utf-8
"""
@author:Xiaozhan Li
@Email:lxz_20081025@163.com
@time:3/28/2023 12:17 PM
@project:HCAPI
"""
# how to use this: [xli3@pek-vx-29075 utils]$ python3 trial_40G.py
from XL710 import Test40G
if __name__ == "__main__":
    tst = Test40G()
    tst.config_tgt()
    tst.start_iperf()
    # tx
    tst.test_tcp_64()
    tst.test_tcp_1024()
    tst.test_tcp_65536()
    tst.test_udp_1400()
    # rx
    tst.test_tcp_rx_64()
    tst.test_tcp_rx_1024()
    tst.test_tcp_rx_65536()
    tst.test_udp_rx_1400()
    # finish test
    tst.close_tgt()
    # process result
    tst.process_iperf_result()


