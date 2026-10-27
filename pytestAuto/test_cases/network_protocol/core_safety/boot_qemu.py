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
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage


class BootQemu(object):
    image_path = None  # different test suite has different path
    t_lx = None
    vx_targets = None
    lxprompt = r'ubuntu@ubuntu:~\$ '   # xiaozhan, this is the sore point
    vxprompt = '# '
    t1 = t2 = t3 = t4 = t5 = t6 = None
    result = None
    pass_num = fail_num = 0

    def setup_class(self):
        self.result = []   # store test case name and result
        # set up network on qemu
        lximage = LinuxImage('/home/xli3/pytestAuto/config/focal-server-cloudimg-amd64.img')
        self.t_lx = QemuTarget('QEMU-LX-1', logFile='linuxqemu.log')
        self.t_lx.boot(lximage)

        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 7)]
        [x.boot(vximage) for x in self.vx_targets]

        # qemu VxWorks
        self.t1, self.t2, self.t3, self.t4, self.t5, self.t6 = self.vx_targets
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::3 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.3 prefixlen 24 up', self.vxprompt)

        # TODO, debug xiaozhan, below is not ok on qemu
        # self.t1.sendAndExpect('sysctl -w net.inet.forwarding = 1', self.vxprompt)
        # self.t1.sendAndExpect('sysctl -w net.inet6.forwarding = 1', self.vxprompt)

        # ret = self.t1.sendAndReturnAll('sysctl -w net.inet.forwarding = 1', self.vxprompt)
        # print(f'=======sysctl -w net.inet.forwarding = 1 is=========\n', ret)
        #
        # ret = self.t1.sendAndReturnAll('sysctl -w net.inet6.forwarding = 1', self.vxprompt)
        # print(f'=======sysctl -w net.inet6.forwarding = 1 is=========\n', ret)

        self.t2.sendAndExpect('cmd', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet6 add 2000::4 prefixlen 64 up', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet add 10.236.1.4 prefixlen 24 up', self.vxprompt)
        #
        self.t3.sendAndExpect('cmd', self.vxprompt)
        self.t3.sendAndExpect('ifconfig eth0 inet6 add 2000::5 prefixlen 64 up', self.vxprompt)
        #
        self.t4.sendAndExpect('cmd', self.vxprompt)
        self.t4.sendAndExpect('ifconfig eth0 inet6 add 2000::6 prefixlen 64 up', self.vxprompt)
        #
        self.t5.sendAndExpect('cmd', self.vxprompt)
        self.t5.sendAndExpect('ifconfig eth0 inet6 add 2000::7 prefixlen 64 up', self.vxprompt)
        #
        self.t6.sendAndExpect('cmd', self.vxprompt)
        self.t6.sendAndExpect('ifconfig eth0 inet6 add 2000::8 prefixlen 64 up', self.vxprompt)

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
        # clean up linux----xiaozhan, this must be after vxworks cleanup
        self.t_lx.cleanup()
        self.t_lx.logFile.close()
        # process self.result ----store result,upload to Database or sth like that
        for i in self.result:
            if i[1] == 'PASS':
                self.pass_num += 1
            else:
                self.fail_num += 1
        log.info(self.result)
        log.info(f'total:{len(self.result)}, pass:{self.pass_num}, fail:{self.fail_num}')


if __name__ == "__main__":
    pass
