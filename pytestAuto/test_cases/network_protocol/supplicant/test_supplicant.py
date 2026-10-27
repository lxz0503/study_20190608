#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:2/4/2024 6:49 PM
@file:test_supplicant.py
"""

import time

import allure
import pytest
import sys

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from test_cases.network_protocol.supplicant.boot_qemu import BootQemu


class Test8021x(BootQemu):
    # name = 'supplicant.supplicant.cmd - IPv4'
    @allure.title('supplicant supplicant cmd IPv4')
    def test_8021x_supplicant_cmd(self):
        with allure.step('supplicant supplicant cmd IPv4'):
            a = self.t1

            ret = '\n'.join(a.sendAndReturnAll('sysvar set -co ip8021x.if_name "simtest-eth0-loopback"', self.vxprompt))
            print(f'====ret is ===== {ret}')
            assert 'ok' in ret

            ret = '\n'.join(a.sendAndReturnAll('ipd kill ip8021x', self.vxprompt))
            print(f'====ret is===={ret}')
            assert 'ipd: kill ip8021x ok' in ret

            ret = '\n'.join(a.sendAndReturnAll('ipd start ip8021x', self.vxprompt))
            print(f'====ret is===={ret}')
            assert 'ipd: start ip8021x ok' in ret

            ret = '\n'.join(a.sendAndReturnAll('supplicant list', self.vxprompt))
            print(f'====ret is===={ret}')
            assert 'suppId = 0, interface = simtest-eth0-loopback, INITIALIZED' in ret

            a.sendAndExpect('supplicant delete 0', self.vxprompt)

            a.sendAndExpect('supplicant add', self.vxprompt)

            ret = a.sendAndReturnAll('ipd reconfigure ip8021x', self.vxprompt)
            print(f'====ret is===={ret}')
            assert 'ipd: reconfigure ip8021x ok' in ret

            ret = a.sendAndReturnAll('supplicant list', self.vxprompt)
            print(f'====ret is ===={ret}')
            assert 'suppId = 0, interface = simtest-eth0-loopback, INITIALIZED' in ret

            a.sendAndExpect('supplicant connect 0', self.vxprompt)

            ret = a.sendAndReturnAll('supplicant getstatus 0;\n', self.vxprompt)
            print(f'====ret is ===={ret}')
            assert 'SM state = CONNECTING' in ret

            a.sendAndExpect('supplicant disconnect 0', self.vxprompt)

            ret = a.sendAndReturnAll('supplicant getstatus 0;\n', self.vxprompt)
            print(f'====ret is ===={ret}')
            assert 'SM state = DISCONNECTING' in ret

            a.sendAndExpect('supplicant logoff 0', self.vxprompt)

            ret = a.sendAndReturnAll('supplicant getstatus 0;\n', self.vxprompt)
            print(f'====ret is ===={ret}')
            assert 'SM state = DISCONNECTING' in ret




if __name__ == "__main__":
    pass
