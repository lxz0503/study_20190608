#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 3/10/2023 4:13 PM
# @Email = lxz_20081025@163.com
# @Name = parser_iperf.py
import re


def parser_iperf(rets, Tx):
    print('rets:', rets)
    #for i in rets:
        #print(i)
    print('key result 64:', rets[-1])
    print('key result 64:', rets[-2])
    pattern = r'\[\s+\d\].*?Bytes\s+(\d+)\s+Mbits/sec.*?sender'
    regex = re.compile(pattern)
    if Tx is True:
        try:
            res_tx = re.match(regex, rets[-2])
        except Exception as e:
            print('tx result is', res_tx)
        else:
            return res_tx.group(1)
    else:
        try:
            res_rx = re.match(regex, rets[-1])
        except Exception as e:
            print('rx result is', res_rx)
        else:
            return res_rx.group(1)

if __name__ == '__main__':
    rets = ['-> sp iperf3,"-c 192.168.10.1 -t 20 -p 10000 -i 20 -l 1400 -f m -b 0 -u"', 'Task spawned: id = 0xffff8000009ddfc0, name = t1', 'value = -140737478008896 = 0xffff8000009ddfc0', '-> Connecting to host 192.168.10.1, port 10000', '[  9] local 192.168.10.3 port 53710 connected to 192.168.10.1 port 10000', '[ ID] Interval           Transfer     Bitrate         Total Datagrams', '[  9]   0.00-20.00  sec  2.18 GBytes   937 Mbits/sec  1673160', '- - - - - - - - - - - - - - - - - - - - - - - - -', '[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams', '[  9]   0.00-20.00  sec  2.18 GBytes   937 Mbits/sec  0.000 ms  0/1673160 (0%)  sender', '[  9]   0.00-20.00  sec  2.18 GBytes   937 Mbits/sec  0.762 ms  0/1673156 (0%)  receiver']
    Tx = True

    print(parser_iperf(rets, Tx))
