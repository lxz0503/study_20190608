#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:1/30/2024 10:28 AM
@file:boot_qemu.py
"""
import sys


from utils.log_record import log
from utils.ezTargets import QemuTarget, VxWorksImage


class BootQemu(object):
    image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-socktest/vxWorks'  # different test suite has different path
    vx_targets = None
    vxprompt = '# '
    t1 = t2 = None
    result = None
    pass_num = fail_num = 0

    def setup_class(self):
        self.result = []   # store test case name and result

        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 3)]
        [x.boot(vximage) for x in self.vx_targets]

        # qemu VxWorks
        self.t1, self.t2 = self.vx_targets
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::3 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.3 prefixlen 24 up', self.vxprompt)

        self.t2.sendAndExpect('cmd', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet6 add 2000::4 prefixlen 64 up', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet add 10.236.1.4 prefixlen 24 up', self.vxprompt)

        # check network connectivity
        # print(f'\n1. run command at Linux target ======{self.t_lx.board}')
        # ret = self.t_lx.sendAndReturnAll('uname -a', self.lxprompt)
        # print('======linux output is======', ret)
        #
        # # input('=====debug=======')
        # print(f'\n2. run command at {self.t1.board}')
        # ret = self.t1.sendAndReturnAll('ifconfig -a', self.vxprompt)
        # print(f'=======ifconfig content is=========\n', ret)
        #
        # print(f'\n3. run command at {self.t2.board}')
        # ret = self.t2.sendAndReturnAll('ifconfig -a', self.vxprompt)
        # print(f'=======ifconfig content is=========\n', ret)
        # #
        # print(f'\n4. ping vxworks from vxworks at {self.t1.board}')
        # cmd = 'ping -c 2 192.168.123.20'
        # ret = self.t1.sendAndReturnAll(cmd, self.vxprompt)
        # print(f'=======ping content is=========\n', ret)
        # #
        # print(f'\n5. ping Linux from vxworks at {self.t1.board}')
        # cmd = 'ping -c 2 192.168.123.80'
        # ret = self.t1.sendAndReturnAll(cmd, self.vxprompt)
        # print(f'=======ping content is=========\n', ret)
        # #
        # print(f'\n6. ping6 vx from vxworks {self.t2.board}')
        # cmd = 'ping6 -c 2 2000::3'
        # ret = self.t2.sendAndReturnAll(cmd, self.vxprompt)
        # print(f'=======ping6 content is=========\n', ret)
        # #
        # print(f'\n7. ping Linux from vxworks {self.t1.board}')
        # cmd = 'ping6 -c 2 2000::2'
        # ret = self.t1.sendAndReturnAll(cmd, self.vxprompt)
        # print(f'=======ping6 content is=========\n', ret)
        # #
        # print(f'\n8. Linux show {self.t_lx.board}')
        # cmd = 'ip addr show'
        # ret = self.t_lx.sendAndReturnAll(cmd, self.lxprompt)
        # print(f'=======Linux show IP=========\n', ret)

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
        log.info(self.result)      # xiaozhan, i[0] is case name, i[1] is pass or fail
        log.info(f'total:{len(self.result)}, pass:{self.pass_num}, fail:{self.fail_num}')


if __name__ == "__main__":
    pass
