#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:5/7/2024 4:30 PM
@file:test_rohc_ip.py
"""
import time
import sys
import re

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage


def echo_server(dut, ip2=None, vxprompt='# ', proto='udp', bufsize=8192, port=7301, echo_once=False, reuse_addr=False,
                limit_recv=0):
    """for ipcom shell"""
    if not ip2:
        ip2 = ip()
    else:
        ip2 = ip(ip2)
    if echo_once:
        echo_once = '-x '
    else:
        echo_once = ''
    if reuse_addr:
        reuse_addr = '-k '
    else:
        reuse_addr = ''

    dut.send('echoserver -t %s -b %s -p %s -L %s %s %s %s' % (
        proto, bufsize, port, limit_recv, echo_once, reuse_addr, ip2.addr))
    if proto == 'raw':
        dut.expect(['echoserver is now listening at %s.*' % ip2.addr,
                    'echoserver is now listening at %s.*' % (ip2.addr.upper())])
    else:
        dut.expect(['echoserver is now listening at %s.%s' % (ip2.addr, port),
                    'echoserver is now listening at %s.%s' % (ip2.addr.upper(), port)])
    dut.expect(vxprompt)


def echo_client(dut, ip2, vxprompt='# ', read_reply=True, connect_before_send=True, reuse_addr=False,
                verify_data=False, succeed=True, proto='udp', connection_refused=False,
                network_unreachable=False, bufsize=8192, nbuf=1, chunk_size=4096,
                timeout=-1, local_port=0, port=7301, limit_recv=0):
    if read_reply:
        read_reply = '-r '
    else:
        read_reply = ''
    if connect_before_send:
        connect_before_send = '-c '
    else:
        connect_before_send = ''
    if verify_data:
        verify_data = '-v '
    else:
        verify_data = ''
    if reuse_addr:
        reuse_addr = '-k '
    else:
        reuse_addr = ''
    if connection_refused:
        succeed = False

    ip2 = ip(ip2)
    dut.send('echoclient %s %s %s -t %s -b %s -n %s -s %s -L %s %s -j %s -p %s %s '
             % (verify_data, read_reply, connect_before_send,
                proto, bufsize, nbuf, chunk_size, limit_recv, reuse_addr,
                local_port, port, ip2.addr))
    if succeed is False:
        if connection_refused:
            dut.expect(self.sh.ECONNREFUSED, timeout)
        elif network_unreachable:
            dut.expect(self.sh.ENETUNREACH, timeout)
        else:
            dut.expect(['Failed to recv data: ' + self.sh.EWOULDBLOCK,
                        'Failed to recv data: ' + self.sh.EAGAIN], timeout)
    else:
        dut.expect('Received %s bytes' % (nbuf * chunk_size,), timeout)
    dut.expect(vxprompt)


def stop_echoserver(dut, vxprompt='# '):
    dut.sendAndExpect('echoserver -q', 'Stopped')
    dut.expect(vxprompt)
