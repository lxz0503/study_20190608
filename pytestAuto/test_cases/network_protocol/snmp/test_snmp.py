#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/24/2024 4:30 PM
@file:test_snmp.py
"""
import allure
import pytest
import sys
import time


from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage


class TestSNMP(object):
    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-snmp/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'snmp'
        self.lxprompt = r'ubuntu@ubuntu:~\$ '  # xiaozhan, must has \$
        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 3)]
        [x.boot(vximage) for x in self.vx_targets]

        lximage = LinuxImage('/home/xli3/pytestAuto/config/focal-server-cloudimg-amd64.img')
        self.t_lx = [QemuTarget('QEMU-LX-%s' % x, logFile='linuxqemu%s.log' % x) for x in range(1, 4)]
        [x.boot(lximage) for x in self.t_lx]

        # qemu VxWorks
        self.t1, self.t2 = self.vx_targets
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::10 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.10 prefixlen 24 up', self.vxprompt)

        self.t2.sendAndExpect('cmd', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet6 add 2000::20 prefixlen 64 up', self.vxprompt)
        self.t2.sendAndExpect('ifconfig eth0 inet add 10.236.1.20 prefixlen 24 up', self.vxprompt)
        # TODO configure IP address for qemu linux

        # qemu linux    # TODO xiaozhan need to modify architecture to support 3 qemu linux
        self.l1, self.l2, self.l3 = self.t_lx
        # IP address for every target
        self.t1_ip, self.t1_ip6 = self.t1.get_ip()
        self.t2_ip, self.t2_ip6 = self.t2.get_ip()
        self.l1_ip, self.l1_ip6 = self.l1.get_ip()

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_agentx_session_limit(self, version):
        with allure.step('snmp agentX test'):
            self.telnetprompt = 'telnet>'
            # self.require_types = ['linux', 'linux', 'linux', 'ipnet']
            # the precondition is VIP parameter SNMP_AGENTX_MAX_SESSIONS = 1
            # note: port 705 is the agentX reserved port
            c1, c2, c3, s = self.l1, self.l2, self.l3, self.t1  # 3 linux and 1 vxworks
            name = 'snmp_agentx_session_limit'
            case_name = self.module + '.' + 'snmp_agentx' + '.' + name + '-' + version

            try:
                # the first linux client telnet to VxWorks port 705
                c1.send('corktelnet %s 705' % self.t1_ip)
                c1.expect('Connected to %s.' % self.t1_ip)
                c1.expect('Escape character is \'^]\'.')
                # c1.send_ctrl_right_square_bracket()
                c1.sendAndExpect('\x1d', self.telnetprompt)   # xiaozhan
                time.sleep(5)

                # the second linux client telnet to VxWorks port 705 and is refused
                c2.send('corktelnet %s 705' % self.t1_ip)
                c2.expect('Connected to %s.' % self.t1_ip)
                c2.expect('Escape character is \'^]\'.')
                c2.expect('Connection closed by foreign host.')
                c2.expect(self.lxprompt)
                time.sleep(5)

                # disconnect the telnet session from the first linux client
                c1.send('quit')
                c1.expect('Connection closed.')

                # the third linux client telnet to VxWorks port 705 and succeed
                c3.send('corktelnet %s 705' % self.t1_ip)
                c3.expect(r'Connected to %s.' % self.t1_ip)
                c3.expect('Escape character is \'^]\'.')
                # c3.send_ctrl_right_square_bracket()
                c3.sendAndExpect('\x1d', self.telnetprompt)
                time.sleep(5)

                c3.send('quit')
                c3.expect('Connection closed.')
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_manager_cmd(self, version):
        with allure.step('snmp_manager_cmd'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_manager_cmd'
            case_name = self.module + '.' + 'snmp_v1_v2' + '.' + name + '-' + version
            try:
                c.sendAndExpect('C snmptalk', self.prompt)
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("port 161")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("version")
                c.expect("version 1|2c <read_community> <write_community>")
                c.sendAndExpect("version 1 public private", self.prompt)
                c.sendAndExpect("status", "version:1")
                c.send("status")
                c.expect("read community:public")
                c.send("help")
                c.expect("Command is any interactive command followed by its arguments.")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                c.send("set sysName.0 interpeak")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("next sysName.0")
                c.expect("sysLocation.0    	String")
                c.sendAndExpect("walk", "No more in MIB", timeout=120)
                c.send("quit")
                c.expect("exit snmptalk cmdline.")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v2c_udp(self, version):
        with allure.step('snmp v2c udp transport test'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_v2c_udp'
            case_name = self.module + '.' + 'snmp_v1_v2' + '.' + name + '-' + version

            try:
                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.sendAndExpect("version 2c public private", self.prompt)
                c.send("status", "version:2c")
                c.send("status")
                c.expect("write community:private")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                c.send("set sysName.0 interpeak")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("next sysName.0")
                c.expect("sysLocation.0    	String")
                c.sendAndExpect("walk", "No more in MIB", timeout=120)
                c.send("quit")
                c.expect("exit snmptalk cmdline.")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v3_peer_id_probe_tsm(self, version):
        with allure.step('snmp version 3 peerId probe in TSM'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_v3_peerId_probe_tsm'
            case_name = self.module + '.' + 'snmp_v3' + '.' + name + '-' + version
            try:
                # copy snmp config files to targets
                # xiaozhan, modify
                c.sendAndExpect('cp /romfs/* /ram', self.vxprompt)
                s.sendAndExpect('cp /romfs/* /ram', self.vxprompt)

                # import snmpserver key and restart SNMP TLS transport
                s.sendAndExpect("keydb import key snmpserver /ram/snmpserver.key", self.vxprompt)
                s.send("keydb import key snmpserver /ram/snmpserver.key", self.vxprompt)
                s.expect("Failed: already installed")
                # Restart SNMP TLS/DTLS transport.
                s.sendAndExpect("C snmp_tls_restart", self.vxprompt)
                # time.sleep(1)
                # comment out this line for we may get a blank line at first and
                # then we will get another "Successfully to restart SNMP TLS model" line.
                # s.expect("Successfully to restart SNMP TLS model")

                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("con_id x 0000000c000000007f000002")
                c.send("status")
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("port 10161")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.sendAndExpect("version 3 TLS", self.prompt)
                c.sendAndExpect("tls_localcert /ram/snmpclient.crt", self.prompt)
                c.sendAndExpect("tls_localkey /ram/snmpclient.key", self.prompt)
                c.sendAndExpect("tls_peercert /ram/snmpserver.crt", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:TLS")
                c.send("status")
                c.expect("at port 10161")
                c.send("status")
                c.expect("peer cert file:/ram/snmpserver.crt")
                c.send("status")
                c.expect("local cert file:/ram/snmpclient.crt")
                c.send("status")
                c.expect("local key file:/ram/snmpclient.key")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                c.send("status")
                c.send("set sysName.0 interpeak")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")

                # run DTLS tests
                c.sendAndExpect("version 3 DTLS", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:DTLS")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("set sysName.0 dtlsserver")
                c.expect("sysName.0    	String(10): dtlsserver")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(10): dtlsserver")

                c.send("quit")
                c.expect("exit snmptalk cmdline.")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v3_peer_id_probe_usm(self, version):
        with allure.step('snmp version 3 peerId probe in USM'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_v3_peerId_probe_usm'
            case_name = self.module + '.' + 'snmp_v3' + '.' + name + '-' + version
            try:
                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("sec_id x 0000000c000000007f000002")
                c.send("status")
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("port 161")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("version 3 UDP initialmd5  authPriv md5 initialmd5 des initialmd5", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:UDP")
                c.send("status")
                c.expect("tos:authPriv, user name:initialmd5")
                c.send("status")
                c.expect("at port 161")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                c.send("status")
                c.send("set sysName.0 interpeak")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("quit")
                c.expect("exit snmptalk cmdline.")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v3_ssh_user_by_pass(self, version):
        with allure.step('snmp version 3 ssh transport authPriv test with username and password'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_v3_SSH_user_by_pass'
            case_name = self.module + '.' + 'snmp_v3' + '.' + name + '-' + version
            try:
                # start server SSH task
                s.sendAndExpect('ipd start ipssh', self.vxprompt)
                time.sleep(1)

                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("port 22")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.sendAndExpect("version 3 SSH", self.prompt)
                c.sendAndExpect("ssh_user ftp interpeak", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:SSH")
                c.send("status")
                c.expect("at port 22")
                c.send("status")
                c.expect("ssh user name:ftp")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                c.send("set sysName.0 interpeak")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")

                c.send("quit")
                c.expect("exit snmptalk cmdline.")

                s.sendAndExpect('ipd kill ipssh', self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v3_ssh_user_keyfile(self, version):
        with allure.step('snmp version 3 ssh transport authPriv test with ssh key file'):
            self.prompt = "snmptalk"
            self.username = "revo"
            self.keyfilepass = "123456"
            c, s = self.t1, self.t2
            name = 'snmp_v3_SSH_user_keyfile'
            case_name = self.module + '.' + 'snmp_v3' + '.' + name + '-' + version
            try:
                # start server SSH task
                s.sendAndExpect('ipd start ipssh', self.vxprompt)
                time.sleep(1)

                # copy snmp config files to targets
                # xiaozhan, modify
                c.sendAndExpect('cp /romfs/* /ram/', self.vxprompt)
                s.sendAndExpect('cp /romfs/* /ram/', self.vxprompt)

                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("port 22")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.sendAndExpect("version 3 SSH", self.prompt)
                c.sendAndExpect("ssh_user %s 123456" % self.username, self.prompt)
                c.sendAndExpect("ssh_key /ram/id_rsa", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:SSH")
                c.send("status")
                c.expect("at port 22")
                c.send("status")
                c.expect("ssh user name:%s" % self.username)
                c.send("status")
                c.expect("ssh key file:/ram/id_rsa")
                c.send("get sysName.0")
                c.expect("Enter PEM pass phrase:")
                c.send("%s" % self.keyfilepass)
                c.expect("sysName.0    	String")

                c.send("quit")
                c.expect("exit snmptalk cmdline.")

                s.sendAndExpect('ipd kill ipssh', self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v3_ssh_tls_dtls(self, version):
        with allure.step('snmp version 3 TLS/DTLS transport authPriv test with cert/key file'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_v3_ssh_tls_dtls'
            case_name = self.module + '.' + 'snmp_v3' + '.' + name + '-' + version
            try:
                # copy snmp config files to targets
                # xiaozhan, modify
                c.sendAndExpect('cp /romfs/* /ram/', self.vxprompt)
                s.sendAndExpect('cp /romfs/* /ram/', self.vxprompt)

                # import snmpserver key and restart SNMP TLS transport
                s.sendAndExpect("keydb import key snmpserver /ram/snmpserver.key", self.vxprompt)
                s.send("keydb import key snmpserver /ram/snmpserver.key")
                s.expect("Failed: already installed")
                # Restart SNMP TLS/DTLS transport.
                s.sendAndExpect("C snmp_tls_restart", self.vxprompt)
                # time.sleep(1)
                # comment out this line for we may get a blank line at first and
                # then we will get another "Successfully to restart SNMP TLS model" line.
                # s.expect_exact("Successfully to restart SNMP TLS model")

                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("port 10161")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.sendAndExpect("version 3 TLS", self.prompt)
                c.sendAndExpect("tls_localcert /ram/snmpclient.crt", self.prompt)
                c.sendAndExpect("tls_localkey /ram/snmpclient.key", self.prompt)
                c.sendAndExpect("tls_peercert /ram/snmpserver.crt", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:TLS")
                c.send("status")
                c.expect("at port 10161")
                c.send("status")
                c.expect("peer cert file:/ram/snmpserver.crt")
                c.send("status")
                c.expect("local cert file:/ram/snmpclient.crt")
                c.send("status")
                c.expect("local key file:/ram/snmpclient.key")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                c.send("set sysName.0 interpeak")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")

                # run DTLS tests
                c.sendAndExpect("version 3 DTLS", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:DTLS")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("set sysName.0 dtlsserver")
                c.expect("sysName.0    	String(10): dtlsserver")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(10): dtlsserver")

                c.send("quit")
                c.expect("exit snmptalk cmdline.")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v3_udp_auth_no_priv(self, version):
        with allure.step('snmp version 3 udp transport authNoPriv test'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_v3_udp_authNoPriv'
            case_name = self.module + '.' + 'snmp_v3' + '.' + name + '-' + version
            try:
                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("port 161")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.sendAndExpect("version 3 UDP initialmd5 authNoPriv md5 initialmd5", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:UDP")
                c.send("status")
                c.expect("tos:authNoPriv, user name:initialmd5")
                c.send("status")
                c.expect("at port 161")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                c.send("set sysName.0 interpeak")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")
                # use sha
                c.sendAndExpect("version 3 UDP initialsha authNoPriv sha initialsha", self.prompt)
                c.send("status")
                c.expect("tos:authNoPriv, user name:initialsha")
                c.send("next sysName.0")
                c.expect("sysLocation.0    	String")
                c.send("quit")
                c.expect("exit snmptalk cmdline.")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v3_udp_auth_priv(self, version):
        with allure.step('snmp version 3 udp transport authPriv test'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_v3_udp_authPriv'
            case_name = self.module + '.' + 'snmp_v3' + '.' + name + '-' + version
            try:
                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("dest %s" % self.t2_ip)
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.send("port 161")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.sendAndExpect("version 3 UDP initialmd5  authPriv md5 initialmd5 des initialmd5", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:UDP")
                c.send("status")
                c.expect("tos:authPriv, user name:initialmd5")
                c.send("status")
                c.expect("at port 161")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                c.send("set sysName.0 interpeak")
                c.expect("sysName.0    	String(9): interpeak")
                c.send("get sysName.0")
                c.expect("sysName.0    	String(9): interpeak")

                c.send("quit")
                c.expect("exit snmptalk cmdline.")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_snmp_v3_udp_no_auth_no_priv(self, version):
        with allure.step('snmp version 3 udp transport test'):
            self.prompt = "snmptalk"
            c, s = self.t1, self.t2
            name = 'snmp_v3_udp_noAuthNoPriv'
            case_name = self.module + '.' + 'snmp_v3' + '.' + name + '-' + version
            try:
                c.sendAndExpect("C snmptalk", self.prompt)
                c.send("dest %s" % self.t2_ip)
                c.expect_exact("snmptalk@%s>" % self.t2_ip)
                c.send("port 161")
                c.expect("snmptalk@%s>" % self.t2_ip)
                c.sendAndExpect("version 3 UDP initialmd5 noAuthNoPriv", self.prompt)
                c.send("status")
                c.expect("version:3 transport mode:UDP")
                c.send("status")
                c.expect("tos:noAuthNoPriv, user name:initialmd5")
                c.send("status")
                c.expect("at port 161")
                c.send("get sysName.0")
                c.expect("sysName.0    	String")
                # should failed for setting is not allowed in noAuthNopriv
                c.send("set sysName.0 interpeak")
                c.expect("SNMP agent reports `authorization error'")
                c.send("next sysName.0")
                c.expect("sysLocation.0    	String")
                c.sendAndExpect("walk", "No more in MIB", timeout=120)
                c.send("quit")
                c.expect("exit snmptalk cmdline.")
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
        for t in self.t_lx:
            t.cleanup()
            t.logFile.close()
        # process self.result ----store result,upload to Database or sth like that
        for i in self.result:
            if i[1] == 'PASS':
                self.pass_num += 1
            else:
                self.fail_num += 1
        log.info(self.result)
        log.info(f'total:{len(self.result)}, pass:{self.pass_num}, fail:{self.fail_num}')
