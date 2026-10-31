#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:1/20/2024 4:30 PM
@file:test_tftp.py
"""
import time
import allure
import pytest
import sys
import os


from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage


def verify_existence(lines, file_name):
    """Verify existence of file "filename\""""
    log.info(f'Verify existence of file {file_name}')
    for i in range(len(lines)):
        line = lines[i]
        files = str.split(line)  # xiaozhan,
        for j in range(len(files)):
            if os.path.basename(files[j]).lower() == file_name:
                return True
    else:
        return False


class TestTFTP(object):
    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-tftp/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'iptftp.tftp'
        self.lxprompt = r'ubuntu@ubuntu:~\$ '    # xiaozhan, must has \$
        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 3)]
        [x.boot(vximage) for x in self.vx_targets]

        lximage = LinuxImage('/home/xli3/pytestAuto/config/focal-server-cloudimg-amd64.img')
        self.t_lx = QemuTarget('QEMU-LX-1', logFile='linuxqemu.log')
        self.t_lx.boot(lximage)

        # qemu VxWorks
        self.t1, self.t2 = self.vx_targets
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::10 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.10 prefixlen 24 up', self.vxprompt)

        self.t2.sendAndExpect('cmd', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet6 add 2000::20 prefixlen 64 up', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet add 10.236.1.20 prefixlen 24 up', self.vxprompt)

        # print(f'\n5. ping Linux from vxworks at {self.t1.board}')
        # cmd = 'ping -c 2 192.168.123.80'
        # ret = self.t1.sendAndReturnAll(cmd, self.vxprompt)
        # print(f'=======ping content is=========\n', ret)
        #
        # print(f'\n5. ping Linux from vxworks at {self.t2.board}')
        # cmd = 'ping -c 2 192.168.123.80'
        # ret = self.t2.sendAndReturnAll(cmd, self.vxprompt)
        # print(f'=======ping content is=========\n', ret)
        #
        # print(f'\n7. ping Linux from vxworks {self.t1.board}')
        # cmd = 'ping6 -c 2 2000::80'
        # ret = self.t1.sendAndReturnAll(cmd, self.vxprompt)
        # print(f'=======ping6 content is=========\n', ret)
        #
        # print(f'\n8. Linux show {self.t_lx.board}')
        # cmd = 'ip addr show'
        # ret = self.t_lx.sendAndReturnAll(cmd, self.lxprompt)
        # print(f'=======Linux show IP=========\n', ret)

        # xiaozhan,
        self.t1_ip, self.t1_ip6 = self.t1.get_ip()
        self.t2_ip, self.t2_ip6 = self.t2.get_ip()
        self.lx_ip, self.lx_ip6 = self.t_lx.get_ip()

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_linux_is_server(self, version):
        with allure.step('TFTP client and server (ipnet client)'):
            a, b, linux = self.t1, self.t2, self.t_lx
            name = 'tftp_linux_is_server'
            case_name = self.module + '.' + name + '-' + version

            try:
                # enabled allow.upload
                a.sendAndExpect('sysvar set -co iptftps.allow.upload "enable"', self.vxprompt)
                b.sendAndExpect('sysvar set -co iptftps.allow.upload "enable"', self.vxprompt)

                # xiaozhan, add, put files to vx tftp root dir-- copy from /romfs/* to /ram/tftpdir
                a.sendAndExpect('cp /romfs/* /ram/tftpdir/', self.vxprompt)
                a.sendAndExpect('ls /ram/tftpdir', self.vxprompt)

                # xiaozhan, add, get files from vx
                file_names = ('tftp0.txt', 'tftp1.txt', 'tftp2.txt', 'tftp0.bin', 'tftp1.bin', 'tftp2.bin')
                for file_name in file_names:
                    linux.sendAndExpect('cd ~/tftpboot', self.lxprompt)
                    linux.send('tftp ' + self.t1_ip + ' get ' + file_name)
                    linux.expect('Transfer completed:')

                lines = linux.sendAndReturnAll('ls', self.lxprompt)
                for file_name in file_names:
                    if verify_existence(lines, file_name):
                        log.error('Failed to get file %s' % file_name)
                        assert False

                # Make sure no tftp test files are present on the target a
                a.sendAndExpect('cd /ram/tftpdir')
                for file_name in file_names:
                    a.sendAndExpect('rm ' + file_name, self.vxprompt)
                    lines = a.sendAndReturnAll('ls', self.vxprompt)
                    if verify_existence(lines, file_name):
                        log.error('File %s not deleted' % file_name)
                        assert False

                # Target a retrieves files from 'linux tftp server'
                for file_name in file_names:
                    a.send('tftp ' + self.lx_ip + ' get ' + file_name)
                    a.expect('Transfer completed:')
                    lines = a.sendAndReturnAll('ls', self.vxprompt)
                    if verify_existence(lines, file_name):
                        log.error('Failed to get file %s' % file_name)
                        assert False

                # Copy files from 'a' to 'b'
                for file_name in file_names:
                    a.send('tftp ' + self.t2_ip + ' put ' + file_name)
                    a.expect('Transfer completed:')
                    lines = b.sendAndReturnAll('ls /ram/tftpdir', self.vxprompt)
                    if not verify_existence(lines, file_name):
                        log.error('Failed to get file %s from target a' % file_name)
                        assert False

                # Copy files from 'b' to 'server'
                for file_name in file_names:
                    b.sendAndExpect('cd /ram/tftpdir', self.vxprompt)
                    b.send('tftp ' + self.lx_ip + ' put ' + file_name + ' ' + file_name + '.copy')
                    b.expect('Transfer completed:')
                    # linux.sendAndExpect('cmp ~/tftpboot/%s.copy ~/tftpcomp/tftpboot/%s' % (file_name, file_name), self.lxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_ipnet_is_server(self, version):
        with allure.step('TFTP client and server (ipnet server)'):
            a, b, linux = self.t1, self.t2, self.t_lx
            name = 'tftp_ipnet_is_server'
            case_name = self.module + '.' + name + '-' + version

            try:
                # enabled allow.upload
                a.sendAndExpect('sysvar set -co iptftps.allow.upload "enable"', self.vxprompt)
                b.sendAndExpect('sysvar set -co iptftps.allow.upload "enable"', self.vxprompt)

                # xiaozhan, add, put files to vx tftp root dir-- copy from /romfs/* to /ram/tftpdir
                a.sendAndExpect('cp /romfs/* /ram/tftpdir/', self.vxprompt)
                a.sendAndExpect('ls /ram/tftpdir', self.vxprompt)

                # xiaozhan, add, get files from vx
                file_names = ('tftp0.txt', 'tftp1.txt', 'tftp2.txt', 'tftp0.bin', 'tftp1.bin', 'tftp2.bin')
                for file_name in file_names:
                    linux.sendAndExpect('cd ~/tftpboot', self.lxprompt)
                    linux.send('tftp ' + self.t1_ip + ' get ' + file_name)
                    linux.expect('Transfer completed:')

                lines = linux.sendAndReturnAll('ls', self.lxprompt)
                for file_name in file_names:
                    if verify_existence(lines, file_name):
                        log.error('Failed to get file %s' % file_name)
                        assert False

                # Make sure no tftp test files are present on the target a
                a.sendAndExpect('cd /ram/tftpdir')
                for file_name in file_names:
                    a.sendAndExpect('rm ' + file_name, self.vxprompt)
                    lines = a.sendAndReturnAll('ls', self.vxprompt)
                    if verify_existence(lines, file_name):
                        log.error('File %s not deleted' % file_name)
                        assert False

                # Send files from linux to ipnet tftp server
                for file_name in file_names:
                    linux.send('atftp --trace -p -r %s -l ~/tftpboot/%s %s' % (file_name, file_name, self.t1_ip))
                    linux.expect('received ACK')
                    lines = a.sendAndReturnAll('ls /ram/tftpdir', self.vxprompt)
                    if verify_existence(lines, file_name) is False:
                        log.error('File %s not found' % file_name)
                        assert False

                # Make sure no tftp test files are present on the target b
                b.sendAndExpect('cd /ram/tftpdir')
                for file_name in file_names:
                    b.sendAndExpect('rm ' + file_name, self.vxprompt)
                    lines = b.sendAndReturnAll('ls', self.vxprompt)
                    if verify_existence(lines, file_name):
                        log.error('File %s not deleted' % file_name)
                        assert False

                # Copy files from 'a' to 'b'
                for file_name in file_names:
                    a.send('tftp ' + self.t2_ip + ' put ' + file_name)
                    a.expect('Transfer completed:')
                    lines = b.sendAndReturnAll('ls /ram/tftpdir', self.vxprompt)
                    if not verify_existence(lines, file_name):
                        log.error('Failed to get file %s from target a' % file_name)
                        assert False

                # Copy files from 'b' to 'server'
                for file_name in file_names:
                    linux.send('atftp --trace -g -r %s -l %s %s' % (file_name, file_name + '.copy', self.t2_ip))
                    linux.expect('sent ACK')
                    # Using md5sum to replace cmp, due to cmp command easy to be added with abnormal characters
                    md5sum1 = '\n'.join(linux.sendAndReturnAll('md5sum %s.copy' % file_name, self.lxprompt)).split(' ')[0]
                    md5sum2 = '\n'.join(linux.sendAndReturnAll('md5sum  ~/tftpboot/%s' % file_name, self.lxprompt)).split(' ')[0]
                    if md5sum1 != md5sum2:
                        log.error('%s tftped not matched original' % file_name)

            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_tftp_no_server(self, version):
        with allure.step('TFTP client without server'):
            a = self.t1
            a.sendAndExpect('tftp', self.vxprompt)
            a.send('tftp -a noserver.interpeak.se get no_server.txt')
            a.expect("Unknown host: noserver.interpeak.se")

    @pytest.mark.parametrize('version', ['IPv6'])
    def test_ipv6_self_is_server(self, version):
        with allure.step('TFTP client and TFTP server (ipnet client)'):
            a, b = self.t1, self.t2
            name = 'tftp_ipv6_self_is_server'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'create.txt'
            try:
                # enabled allow.upload
                a.sendAndExpect('sysvar set -co iptftps.allow.upload "enable"', self.vxprompt)
                b.sendAndExpect('sysvar set -co iptftps.allow.upload "enable"', self.vxprompt)

                # Make sure no tftp test files are present on the target b
                b.sendAndExpect('cd /ram/tftpdir')
                b.sendAndExpect('rm ' + file_name, self.vxprompt)
                lines = b.sendAndReturnAll('ls', self.vxprompt)
                if verify_existence(lines, file_name):
                    log.error('File %s not deleted' % file_name)
                    assert False

                # Create the file in TFTP server b
                b.sendAndExpect('cd /ram/tftpdir', self.vxprompt)
                b.sendAndExpect('tftp -c ' + file_name, self.vxprompt)
                lines = b.send_and_return_all('ls /ram/tftpdir', self.vxprompt)
                if verify_existence(lines, file_name) is False:
                    log.error('File %s not found' % file_name)
                    assert False

                # Make sure no tftp test files are present on the target a
                a.sendAndExpect('cd /ram/tftpdir')
                a.sendAndExpect('rm ' + file_name, self.vxprompt)
                lines = b.sendAndReturnAll('ls', self.vxprompt)
                if verify_existence(lines, file_name):
                    log.error('File %s not deleted' % file_name)
                    assert False

                # Gets files from 'tftp server' b
                a.sendAndExpect('cd /ram/tftpdir', self.vxprompt)
                a.send('tftp ' + self.t2_ip6 + ' get ' + file_name)
                a.expect('Transfer completed:')
                lines = a.sendAndReturnAll('ls', self.vxprompt)
                if verify_existence(lines, file_name) is False:
                    log.error('File %s not found' % file_name)
                    assert False

                # Make sure no tftp test files are present on the target b
                b.sendAndExpect('cd /ram/tftpdir', self.vxprompt)
                b.sendAndExpect('rm ' + file_name, self.vxprompt)
                lines = b.sendAndReturnAll('ls /ram/tftpdir', self.vxprompt)
                if verify_existence(lines, file_name) is True:
                    log.error('File %s not deleted' % file_name)
                    assert False

                # Copy files from 'a' to 'b'
                a.send('tftp ' + self.t2_ip6 + ' put ' + file_name)
                a.expectt('Transfer completed:')
                lines = b.sendAndReturnAll('ls /ram/tftpdir', self.vxprompt)
                if verify_existence(lines, file_name) is False:
                    log.error('File %s not found' % file_name)
                    assert False
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_tftp_check_working_directory(self, version):
        with allure.step('checking working directory'):
            a, b = self.t1, self.t2
            name = 'tftp_check_working_directory'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'check.txt'
            try:
                # enabled allow.upload
                a.sendAndExpect('sysvar set -co iptftps.allow.upload "enable"', self.vxprompt)
                if version == 'IPv6':
                    b.send('tftp ' + self.t1_ip6 + ' get ' + file_name)
                    b.expect("ERROR: Code=2 Msg=\"Could not access file aboved working directory.\"")
                else:
                    b.send('tftp ' + self.t1 + ' get ' + file_name)
                    b.expect("ERROR: Code=2 Msg=\"Could not access file aboved working directory.\"")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

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
    pytest.main(['-s'])
