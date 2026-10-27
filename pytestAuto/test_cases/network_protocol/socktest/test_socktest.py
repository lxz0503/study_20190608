#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:2/21/2024 10:29 AM
@file:test_socktest.py
"""
import pytest
import allure
import sys

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from utils.api import runSockTest
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage


class TestSocktest(object):
    def setup_class(self):
        self.tcp_name = 'socktest.tcp'
        self.tcp_proto = 'tcp'
        self.udp_name = 'socktest.udp'
        self.udp_proto = 'udp'

        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-socktest/vxWorks'  # different test suite has different path
        self.vxprompt = '# '
        self.t1 = self.t2 = None
        self.pass_num = self.fail_num = 0
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

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0010socket(self, version):
        funcname = 'socket'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0010socket'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret  # record test result and test case name
            for i in ret:  # pass or fail for whole suite   i[0] is the case name
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0020bind(self, version):
        funcname = 'bind'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0020bind'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0030connect(self, version):
        funcname = 'connect'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0030connect'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0040accept(self, version):
        funcname = 'accept'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0040accept'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0050getsockname(self, version):
        funcname = 'getsockname'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0050getsockname'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0060getpeername(self, version):
        funcname = 'getpeername'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0060getpeername'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0070send(self, version):
        funcname = 'send'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0070send'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0080sendto(self, version):
        funcname = 'sendto'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0080sendto'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0090sendmsg(self, version):
        funcname = 'sendmsg'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0090sendmsg'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0100recv(self, version):
        funcname = 'recv'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0100recv'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0110recvfrom(self, version):
        funcname = 'recvfrom'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0110recvfrom'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0120recvmsg(self, version):
        funcname = 'recvmsg'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0120recvmsg'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0130ioctl(self, version):
        funcname = 'ioctl'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0130ioctl'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0140select(self, version):
        funcname = 'select'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0140select'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0150shutdown(self, version):
        funcname = 'shutdown'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0150shutdown'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_tcp_c0160close(self, version):
        funcname = 'close'
        with allure.step(f'run %s %s socktest' % (self.tcp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.tcp_name + '.' + 'c0160close'
            ret = runSockTest(self.tcp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0010socket(self, version):
        funcname = 'socket'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0010socket'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0020bind(self, version):
        funcname = 'bind'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0020bind'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0030connect(self, version):
        funcname = 'connect'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0030connect'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0050getsockname(self, version):
        funcname = 'getsockname'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0050getsockname'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0060getpeername(self, version):
        funcname = 'getpeername'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0060getpeername'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0070send(self, version):
        funcname = 'send'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0070send'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0080sendto(self, version):
        funcname = 'sendto'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0080sendto'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0090sendmsg(self, version):
        funcname = 'sendmsg'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0090sendmsg'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0100recv(self, version):
        funcname = 'recv'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0100recv'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0110recvfrom(self, version):
        funcname = 'recvfrom'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0110recvfrom'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0120recvmsg(self, version):
        funcname = 'recvmsg'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0120recvmsg'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0130ioctl(self, version):
        funcname = 'ioctl'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0130ioctl'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0140select(self, version):
        funcname = 'select'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0140select'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0150shutdown(self, version):
        funcname = 'shutdown'
        with allure.step(f'run %s %s socktest' % (self.udp_proto, funcname)):
            a, b = self.t1, self.t2
            parentTestName = self.udp_name + '.' + 'c0150shutdown'
            ret = runSockTest(self.udp_proto, funcname, a, b, version, parentTestName, timeout=60)
            self.result += ret
            for i in ret:  # pass or fail for whole suite
                assert i[1] == 'PASS'

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_socktest_udp_c0170recvmsg_controllen(self, version):
        with allure.step('run udp socket recvmsg controllen test'):
            name = 'c0170recvmsg_controllen'
            case_name = self.udp_name + '.' + name + '-' + version
            s, c = self.t1, self.t2

            s6 = '6' if version == 'IPv6' else ''
            s_ip = '2000::3/64' if version == 'IPv6' else '192.168.123.10/24'

            c_cmd = 'C mysendto%s("%s")' % (s6, s_ip)

            # input('----debug----')    # xiaozhan debug
            # msghdr.msg_controllen set to '1'
            s_cmd = 'C recvmsg_controllen_test%s(1)' % s6
            s.sendAndExpect(s_cmd, 'bind ok.')
            c.sendAndExpect(c_cmd, self.vxprompt)
            try:
                s.expect('test pass')
            except:
                ret = 'FAIL'
                log.error('msg_controllen is not 0 when truncated')
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

            # msghdr.msg_controllen set to '16'
            s_cmd = 'C recvmsg_controllen_test%s(16)' % s6
            s.sendAndExpect(s_cmd, 'bind ok.')
            c.sendAndExpect(c_cmd, self.vxprompt)
            try:
                s.expect('test pass')
            except:
                ret = 'FAIL'
                log.error('recvmsg failed for enough msg_controllen.')
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

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
        log.info('----test result statistics for socktest----')
        log.info(self.result)      # xiaozhan, i[0] is case name, i[1] is pass or fail
        log.info(f'total:{len(self.result)}, pass:{self.pass_num}, fail:{self.fail_num}')


if __name__ == "__main__":
    pass
