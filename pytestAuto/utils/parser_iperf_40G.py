#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 3/10/2023 4:13 PM
# @Email = lxz_20081025@163.com
# @Name = parser_iperf.py
import re


def parser_iperf(rets, Tx):
    print('rets:', rets)
    for i in rets:
        print(i)
    print('key result 64:', rets[7])
    print('key result 64:', rets[6])
    pattern = r'\[\s+\d\].*?Bytes\s+(\d+)\s+Mbits/sec'
    regex = re.compile(pattern)
    if Tx is True:
        try:
            res_tx = re.match(regex, rets[7])
        except Exception as e:
            print('tx result is', res_tx)
        else:
            return res_tx.group(1)
    else:
        try:
            res_rx = re.match(regex, rets[8])
        except Exception as e:
            print('rx result is', res_rx)
        else:
            return res_rx.group(1)

