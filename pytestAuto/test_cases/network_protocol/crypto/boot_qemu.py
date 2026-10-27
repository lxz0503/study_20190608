#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:1/30/2024 10:28 AM
@file:boot_qemu.py
"""
import sys

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from utils.ezTargets import QemuTarget, VxWorksImage


class BootQemu(object):
    image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-crypto/vxWorks'  # different test suite has different path
    vx_targets = None
    vxprompt = '# '
    t1 = None
    result = None
    pass_num = fail_num = 0

    def setup_class(self):
        self.result = []  # store test case name and result
        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 2)]
        [x.boot(vximage) for x in self.vx_targets]
        # qemu VxWorks
        self.t1 = self.vx_targets[0]
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::3 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.3 prefixlen 24 up', self.vxprompt)

        # TODO, debug xiaozhan, below is not ok on qemu

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
        log.info('----test result statistics----')
        log.info(self.result)
        log.info(f'total:{len(self.result)}, passed:{self.pass_num}, failed:{self.fail_num}')


if __name__ == "__main__":
    pass
