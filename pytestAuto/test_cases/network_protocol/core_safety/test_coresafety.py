#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:2/20/2024 5:22 PM
@file:test_coresafety.py
"""

import time
import pytest
import allure
import sys


from utils.log_record import log  # xiaozhan, this is my log module not old kong
from test_cases.network_protocol.core_safety.boot_qemu import BootQemu

FUNC_RET_SUCCESS = 'value = 0 = 0x0'
bStart = False
loopCount = 2500
resultFile = "/ram0/coresafetyresult.txt"


def startServer(ks, rs):
    global bStart
    if bStart:
        return
    # run the upd server in kernel
    ks.send('C sp testStartUdpServer')
    rs.send('C ATestSPRTP("server", "localhost", "1000")')
    bStart = True


def runClient(log, cmd, c):
    log('executing %s' % (cmd))
    ret = c.send_and_return_all(cmd)
    log('%s result: %s' % (cmd, ret))

    time.sleep(90)

    # check the result
    cmd = 'C testGetResult'
    log('executing %s' % (cmd))
    ret = c.send_and_return_all(cmd)
    log('%s result: %s' % (cmd, ret))

    # The 'ret' has lots of other string.
    if ret[-2] != "OK":
        raise test_fail('memory is used up')

    cmd = 'rm %s' % (resultFile)
    c.send(cmd)


class TestCoreSafety(BootQemu):
    """Test the memory is not used up when the server is running in kernel space\
    and the client is running in user space"""

    def config(self):
        self.hosts = 4
        self.eta = 180
        self.v6 = False

    def test_kernel_rtp_no_used_up(self, log, hosts, v6, opt):
        ks, rs, a, b = hosts
        startServer(ks, rs)

        # the client running in the user space sends data to the server
        cmd = 'C ATestSPRTP("client", "%s", "%s")' % (ks.ip().addr, loopCount)
        runClient(log, cmd, a)


if __name__ == "__main__":
    pass
