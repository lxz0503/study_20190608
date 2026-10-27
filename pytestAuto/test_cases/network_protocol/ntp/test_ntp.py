#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/17/2024 4:30 PM
@file:test_ntp.py
"""
import time
import allure
import pytest
import sys
import os
import re
from datetime import date, datetime, timedelta

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage


################################################################################
#        ntpq_send_and_return_all - ntpq cmd
################################################################################
def ntpq_send_and_return_all(ntpq, cmd, prompt='ntpq> ', append=''):
    '''uses pexpect
    returns a list of all lines of output, stripped of crap like leading/trailing whitespace.'''
    ntpq.send(cmd.strip() + append)
    ntpq.expect(prompt)
    all = ntpq.s.s.before

    all = all.replace('\r\n\x00', '')

    lines0 = all.split('\r\n')  # split lines. this is pty style newlines.
    lines0 = lines0[0:]  # all but cmd
    if len(lines0) == 0:
        return []
    lines1 = []
    for a in lines0:
        a = a.strip()
        lines1.append(a)  # strip leading / trailing whitespace
    while len(lines1) > 0 and lines1[0] == '':  # remove any leading empty lines
        lines1 = lines1[1:]
    while len(lines1) > 0 and lines1[-1] == '':  # remove any trailing empty lines
        lines1 = lines1[:-1]
    return lines1


################################################################################
#        ntpdc_send_and_return_all - ntpdc cmd
################################################################################
def ntpdc_send_and_return_all(ntpdc, cmd, prompt='ntpdc> ', append=''):
    '''uses pexpect
    returns a list of all lines of output, stripped of crap like leading/trailing whitespace.'''
    ntpdc.send(cmd.strip() + append)
    ntpdc.expect(prompt)
    all = ntpdc.s.s.before

    all = all.replace('\r\n\x00', '')

    lines0 = all.split('\r\n')  # split lines. this is pty style newlines.
    lines0 = lines0[0:]  # all but cmd
    if len(lines0) == 0:
        return []
    lines1 = []
    for a in lines0:
        a = a.strip()
        lines1.append(a)  # strip leading / trailing whitespace
    while len(lines1) > 0 and lines1[0] == '':  # remove any leading empty lines
        lines1 = lines1[1:]
    while len(lines1) > 0 and lines1[-1] == '':  # remove any trailing empty lines
        lines1 = lines1[:-1]
    return lines1


################################################################################
#        ntp_verify_response - verify ntpq and ntpdc response
################################################################################
def ntp_verify_response(lines, response, offset=0):
    response = response[offset:]

    for i in range(len(lines)):
        line = lines[i]
        if len(line) == 0:
            continue
        if line.find(response) != -1:
            return True
    log.error('Response mismatch (' + line + ' != ' + response)


################################################################################
#        ntp_verify_response_return_assID - verify ntpq and ntpdc response and return assID
################################################################################
def ntp_verify_response_return_assID(lines, response, offset=0):
    response = response[offset:]

    for i in range(len(lines)):
        line = lines[i]
        if len(line) == 0:
            continue
        if line.find(response) != -1:
            line = lines[i + 2]
            item = line.split()
            return item[1]
    log.error('Response mismatch (' + line + ' != ' + response)


################################################################################
#        stop_ntpd - Stop Network Time Protocol Daemon
################################################################################
def stop_ntpd(ntps, prompt):
    ntps.sendAndExpect('pkill -9 ntpd', prompt)


################################################################################
#        ntp_verify_file
################################################################################
def ntp_verify_file(t, filename, prompt):
    lines = t.sendAndReturnAll('ls', prompt)
    for i in range(len(lines)):
        line = lines[i].split()
        if len(line) == 0:
            continue
        for j in range(len(line)):
            if line[j] == filename:
                return True
    else:
        return False


################################################################################
#        ntp_verify_file_fuzzy
################################################################################
def ntp_verify_file_fuzzy(t, fuzzy_filename, prompt):
    lines = t.sendAndReturnAll('ls', prompt)
    for i in range(len(lines)):
        line = lines[i].split()
        if len(line) == 0:
            continue
        for j in range(len(line)):
            if line[j].find(fuzzy_filename) != -1:
                return True
    else:
        return False

    ################################################################################
    #        ntp_gethostname_from_keyfile
    ################################################################################
    ''' The input parameter filename must be fuzzy_filename_hostname '''


def ntp_gethostname_from_file(t, fuzzy_filename):
    lines = t.send_and_return_all('ls')
    for i in range(len(lines)):
        line = lines[i].split()
        if len(line) == 0:
            continue
        for j in range(len(line)):
            pos = line[j].find(fuzzy_filename)
            if pos != -1:
                pos = pos + len(fuzzy_filename)
                return line[j][pos:]
    else:
        return []


################################################################################
#        start_ntpd - Start Network Time Protocol Daemon
################################################################################
from time import sleep


def start_ntpd(ntps, file_name, prompt, ip):
    stop_ntpd(ntps, prompt)

    # try to set clock for 15 minutes then exit
    ntps.sendAndExpect('ntpd -q -c ~/ntp/' + file_name, prompt, timeout=900)
    ntps.sendAndExpect('ntpd -c ~/ntp/' + file_name, prompt, timeout=60)
    res = '\n'.join(ntps.sendAndReturnAll('ps aux', prompt))
    if 'ntpd' not in res:
        log.error('Failed to start ntpd')
        assert False

    # try synchronizing the ntp daemon for 5 minutes
    for _ in range(5 * 60 / 5):
        ntps.send('ntpdate -p 1 -d ' + ip)
        i = ntps.expect(
            ['no server suitable for synchronization found', 'adjust time server', 'step time server'])
        if i == 1 or i == 2:
            break
        time.sleep(5)
    else:
        log.error('no server suitable for synchronization found')
        assert False


################################################################################
#        copy_ntp_config - Copy ntp config files
################################################################################


def wait_cmd_ready(host, cmd, expect_re, prompt, timeout=1200, interval=5):
    ptn = '(?s)' + expect_re    # xiaozhan, cross-line match
    start_time = time.time()
    i = 0

    while True:
        if (time.time() - start_time) >= timeout:
            log.error('timeout after %s seconds' % timeout)
            assert False

        lines = host.sendAndReturnAll(cmd, prompt)
        if re.search(ptn, '\n'.join(lines)) is None:
            time.sleep(interval)
            i += 1
        else:
            break


def get_today():
    return date.today().strftime('%Y-%m-%d')


def after_today(num_from_today):
    assert type(num_from_today) == int
    return (date.today() + timedelta(days=num_from_today)).strftime('%Y-%m-%d')


def get_dates_with_diff_year():
    current_day = get_today()
    this_year = current_day.split('-')[0]
    i = 0
    while True:
        one_year_ago = after_today(-(365 + i))
        last_year = one_year_ago.split('-')[0]
        if this_year != last_year:
            break
    return current_day, one_year_ago


class TestNTP(object):
    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-ntp/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'ipntp.ntp'
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

        self.t1_ip, self.t1_ip6 = self.t1.get_ip()
        self.t2_ip, self.t2_ip6 = self.t2.get_ip()
        self.lx_ip, self.lx_ip6 = self.t_lx.get_ip()

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_ntp_api(self, version):
        with allure.step('IPNTP api'):
            ntpc, ntps = self.t1, self.t_lx  # t, s = hosts
            name = 'api'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.unicasntpc1.conf'
            try:
                if version == 'IPv6':
                    ntpc_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                ntpc.send('ntp -v')
                ntpc.expect("All rights reserved.")
                ntpc.send('ntp')
                ntpc.expect("     The ntp command will exit with 0 on success, and non-zero on errors.")
                ntpc.send('ntp -u')
                ntpc.expect("No ntp server specified!")
                ntpc.send('ntp -t 20 -u ' + ntps_ip)
                ntpc.expect("System time updated")
                ntpc.send('ntp -t 20 -q ' + ntps_ip)
                ntpc.expect("20[0-9][0-9]")
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_daemon_nokey(self, version):
        with allure.step('Test the IPNTP ntpd ntpq ntpdc daemon'):
            ntpc1, ntpc2, ntps = self.t1, self.t2, self.t_lx   # t z s
            name = 'daemon_nokey'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.unicasntpc1.conf'
            try:
                if version == 'IPv6':
                    ntpc1_ip = self.t1_ip6
                    ntpc2_ip = self.t2_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc1_ip = self.t1_ip
                    ntpc2_ip = self.t2_ip
                    ntps_ip = self.lx_ip

                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                # stop ipntp
                ntpc1.sendAndExpect('kill ipd ipntp', self.vxprompt)
                ntpc2.sendAndExpect('kill ipd ipntp', self.vxprompt)

                # set peer invalid time
                # extra long timeout on first date command
                ntpc1.sendAndExpect("date 1999-01-02", 'ok', timeout=300)
                ntpc1.sendAndExpect('date', '1999')

                # start ntp daemon with primary server
                # ntplog=os.path.join(config.productroot, config.productpath['ipntp'], 'test', 'ntp', 'ntp.log')
                cmd1 = f'sysvar set -co ipntp.config.param "server {ntpc2_ip}; disable auth;logfile ntp.log"'
                ntpc1.sendAndExpect(cmd1, self.vxprompt)
                cmd2 = f'sysvar set -co ipntp.config.param "server {ntps_ip}; disable auth;logfile ntp.log"'
                ntpc2.sendAndExpect(cmd2, self.vxprompt)
                ntpc1.sendAndExpect('sysvar set -co ipntp.inintpc1.param "-g -A"', self.vxprompt)
                ntpc2.sendAndExpect('sysvar set -co ipntp.inintpc1.param "-g -A"', self.vxprompt)

                # waiting for synchronizing to the server about 10 minutes
                ntpc2.sendAndExpect('ipd start ipntp', self.vxprompt)
                # verify time
                wait_cmd_ready(ntpc2, 'date', '20[0-9][0-9]')

                # waiting for t synchronize to the z about 10 minutes
                ntpc1.sendAndExpect('ipd start ipntp', self.vxprompt)
                # verify time
                wait_cmd_ready(ntpc1, 'date', '20[0-9][0-9]')
                # ntpc1.sendAndExpect('cat ntp.log')
                # ntpc2.sendAndExpect('cat ntp.log')

                # query state
                ntpc1.sendAndExpect('ntp -p', self.vxprompt)
                # ntpc1.expect_re_and_wait_prompt("st t when poll reach   delay")
                ntpc1.sendAndExpect('ntp -d', self.vxprompt)
                # ntpc1.expect_re_and_wait_prompt("st poll reach  delay   offset")

                # clean
                stop_ntpd(ntps, self.lxprompt)
                # delete local files----xiaozhan,debug--is this log necessary?
                ntpc1.sendAndExpect('rm /ram/ntp.log', self.vxprompt)
                ntpc2.sendAndExpect('rm /ram/ntp.log', self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_daemon_symkey(self, version):
        """IPNTP ntpd with a symmetrical key.
        This tests all the IPNTP daemons.
        1. Set incorrect system time on target.
        2. Start Linux ntpd (broadcast enabled).
        3. Generate MD5 key, hostkey and cert in target t&z
        4. Let target t sychronize with linux.
        5. Let target z sychronize with target t using symmetrical key.
        6. Verify that system time is updated on target t&z"""

        with allure.step('IPNTP ntpd with a symmetrical key'):
            ntpc1, ntpc2, ntps = self.t1, self.t2, self.t_lx  # t z s
            name = 'daemon_symkey'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.unicast.conf'
            try:
                if version == 'IPv6':
                    ntpc1_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc1_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                # stop ipntp
                ntpc1.sendAndExpect('kill ipd ipntp', self.vxprompt)
                ntpc2.sendAndExpect('kill ipd ipntp', self.vxprompt)

                # set target t invalid time
                current_day, one_year_ago = get_dates_with_diff_year()
                this_year = current_day.split('-')[0]
                last_year = one_year_ago.split('-')[0]

                ntpc1.send("date %s" % one_year_ago)
                ntpc1.expect("ok", timeout=300)  # extra long timeout on first date command
                ntpc1.send("date")
                ntpc1.expect(last_year)
                # set target z invalid time
                ntpc2.send("date %s" % one_year_ago)
                ntpc2.expect("ok", timeout=300)  # extra long timeout on first date command
                ntpc2.send("date")
                ntpc2.expect(last_year)

                # copy rand file to target
                # ntps.sendAndExpect('pkill -9 in.tftpd')
                # ntps.sendAndExpect('in.tftpd --daemon ~/ntp/')
                ntpc1.sendAndExpect('tftp ' + ntps_ip + ' get rnd')
                ntpc1.expect('Transfer completed:')
                if ntp_verify_file(ntpc1, 'rnd', self.vxprompt) is False:
                    log.error('Randfile rnd is not existed.')
                    assert False

                # generate MD5 keys
                ntpc1.sendAndExpect('ntpkey -r rnd -M -p password1 -S RSA -s hostname', self.vxprompt)
                time.sleep(10)
                if ntp_verify_file_fuzzy(ntpc1, 'ntp.keys', self.vxprompt) is False:
                    log.error('generate MD5 key' + ' failed')
                    assert False

                # using MD5 keyfile from linux
                ntpc1.send('tftp ' + ntps_ip + ' get ntpkeys')
                ntpc1.expect('Transfer completed:')
                if ntp_verify_file(ntpc1, 'ntpkeys', self.vxprompt) is False:
                    log.error('ntpkeys is not existed.')
                    assert False
                ntpc2.send('tftp ' + ntps_ip + ' get ntpkeys')
                ntpc2.expect('Transfer completed:')
                if ntp_verify_file(ntpc2, 'ntpkeys', self.vxprompt) is False:
                    log.error('ntpkeys is not existed.')
                    assert False

                ntpc2.send('tftp ' + ntps_ip + ' get rnd')
                ntpc2.expect('Transfer completed:')
                if ntp_verify_file(ntpc2, 'rnd', self.vxprompt) is False:
                    log.error('Randfile rnd is not existed.')
                    assert False

                # generate configure file ntp.conf, adding server info into it
                # target s will synchronize with linux target
                ntps.sendAndExpect('cd ntp', self.lxprompt)
                ntps.sendAndExpect('cp ntp.conf ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo server ' + ntps_ip + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo driftfile drift' + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo keys ntpkeys' + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo statsdir ./' + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo logfile ntp.log ' + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo trustedkey 1 ' + '>> ntp.conf', self.lxprompt)

                # target z will synchronize with target s
                ntps.sendAndExpect('echo server ' + ntpc1_ip + ' key 1 ' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo keys ntpkeys' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo statsdir ./' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo logfile ntp.log ' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo trustedkey 1 ' + '>> ntp2.conf', self.lxprompt)

                # download ntp.conf to local
                ntpc1.send('tftp ' + ip + ' get ntp.conf')
                ntpc1.expect('Transfer completed:')
                if ntp_verify_file(ntpc1, 'ntp.conf', self.vxprompt) is False:
                    log.error('ntp.conf is not existed.')
                    assert False
                ntpc2.send('tftp ' + ntps_ip + ' get ntp2.conf')
                ntpc2.expect('Transfer completed:')
                if ntp_verify_file(ntpc2, 'ntp2.conf', self.vxprompt) is False:
                    log.error('ntp2.conf is not existed.')
                    assert False

                # start ntp daemon with configure file
                ntpc1.sendAndExpect('sysvar unset ipntp.config.param', self.vxprompt)
                ntpc2.sendAndExpect('sysvar unset ipntp.config.param', self.vxprompt)
                ntpc1.sendAndExpect('sysvar set -co ipntp.init.param "-c ntp.conf -g"', self.vxprompt)
                ntpc2.sendAndExpect('sysvar set -co ipntp.init.param "-c ntp2.conf -g"', self.vxprompt)
                ntpc1.sendAndExpect('ipd start ipntp', self.vxprompt)
                # waiting for synchronizing to the server about 10 minutes
                # verify time
                wait_cmd_ready(ntpc1, 'date', this_year, self.vxprompt)
                ntpc1.sendAndExpect('cat ntp.log', self.vxprompt)

                # change z hostname
                ntpc2.sendAndExpect('ntpkey -Z ntpclient', self.vxprompt)
                ntpc2.sendAndExpect('ipd start ipntp', self.vxprompt)
                # waiting for z synchronizing to the t about 1 hour
                # at ubuntu 12.04, it can be done with 20 minutes
                # however at ubuntu 18.04, it cannot be done with 1 hours
                wait_cmd_ready(ntpc2, 'date', this_year, self.vxprompt, timeout=3600)
                ntpc2.sendAndExpect('cat ntp.log', self.vxprompt)

                # delete local files---xiaozhan, debug
                ntpc1.sendAndExpect('rm ntp.conf', self.vxprompt)
                ntpc1.sendAndExpect('rm ntp.log', self.vxprompt)
                ntpc1.sendAndExpect('rm rnd', self.vxprompt)
                ntpc1.sendAndExpect('rm ntpkeys', self.vxprompt)
                ntpc1.sendAndExpect('rm ntp.keys', self.vxprompt)
                ntpc2.sendAndExpect('rm ntp2.conf', self.vxprompt)
                ntpc2.sendAndExpect('rm ntp.log', self.vxprompt)
                ntpc2.sendAndExpect('rm rnd', self.vxprompt)
                ntpc2.sendAndExpect('rm ntpkeys', self.vxprompt)
                ntpc2.sendAndExpect('rm ntpkey_cert_ntpclient', self.vxprompt)
                ntpc2.sendAndExpect('rm ntpkey_host_ntpclient', self.vxprompt)
                ntpc1.sendAndExpect('ls', self.vxprompt)
                ntpc2.sendAndExpect('ls', self.vxprompt)

                # clean
                stop_ntpd(ntps, self.lxprompt)

            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_daemon_autokey(self, version):
        """IPNTP ntpd with autokey(GQ and MV scheme).
            This tests all the IPNTP daemons.
            1. Set incorrect system time on target.
            2. Start Linux ntpd (broadcast enabled).
            3. Generate GQ&MV key, hostkey and cert in target t with pass 12345678
            4. Generate hostkey and cert in target z with same pass 12345678
            5. Get GQ&MV key from target t.
            6. Set incorrect time in target t and z.
            7. Let target t sychronize with linux.
            8. Let target z sychronize with target t using autokey.
            9. Verify that system time is updated on target t&z"""
        with allure.step('Test the IPNTP ntpd daemon with autokey'):
            ntpc1, ntpc2, ntps = self.t1, self.t2, self.t_lx  # t z s
            name = 'daemon_autokey'
            case_name = self.module + '.' + name + '-' + version
            file_name = 'ntp.server.unicast.conf'
            try:
                if version == 'IPv6':
                    ntpc1_ip = self.t1_ip6
                    ntps_ip = self.lx_ip6
                else:
                    ntpc1_ip = self.t1_ip
                    ntps_ip = self.lx_ip

                # xiaozhan, copy ntp config from vx
                ntps.sendAndExpect('cd ~/ntp', self.lxprompt)
                ntps.send('tftp ' + ntpc1_ip + ' get ' + file_name)
                ntps.expect('Transfer completed:')

                # xiaozhan, start ntp server
                start_ntpd(ntps, file_name, self.lxprompt, ntps_ip)

                # stop ipntp
                ntpc1.sendAndExpect('kill ipd ipntp', self.vxprompt)
                ntpc2.sendAndExpect('kill ipd ipntp', self.vxprompt)

                # xiaozhan, debug
                # Firstly set t and z to correct time. This latest time
                # will be used to generate certificate for the certficate will
                # be expired in one year.
                ntpc1.send('ntp -t 20 -u ' + ntps_ip)
                ntpc1.expect("System time updated")
                ntpc2.send('ntp -t 20 -u ' + ntps_ip)
                ntpc2.expect("System time updated")

                # copy rand file to target
                ntps.sendAndExpect('pkill -9 in.tftpd', self.lxprompt)
                ntps.sendAndExpect('in.tftpd --daemon ~/ntp/', self.lxprompt)
                # s.send('ps aux')
                # s.expect_exact_and_wait_prompt('in.tftpd')
                # t.ping(s.ip().addr, count=2, retries=5)
                ntpc1.send('tftp ' + ntps_ip + ' get rnd')
                ntpc1.expect('Transfer completed:')
                if ntp_verify_file(ntpc1, 'rnd', self.vxprompt) is False:
                    log.error('Randfile rnd is not existed.')
                    assert False
                # change t hostname
                ntpc1.sendAndExpect('ntpkey -Z ntpserver', self.vxprompt)
                # generate GQkey, MVkey, IFFkey, hostkey and trust cert
                ntpc1.sendAndExpect('ntpkey -r rnd -T -G -V 5 -I -p 12345678', self.vxprompt)
                time.sleep(10)
                if ntp_verify_file_fuzzy(ntpc1, 'ntpkey_cert_', self.vxprompt) is False:
                    log.error('generate ntpkey_cert_' + ' failed')
                    assert False
                if ntp_verify_file_fuzzy(ntpc1, 'ntpkey_host_', self.vxprompt) is False:
                    log.error('generate ntpkey_host_' + ' failed')
                    assert False
                if ntp_verify_file_fuzzy(ntpc1, 'ntpkey_gqkey_', self.vxprompt) is False:
                    log.error('generate ntpkey_gqkey_' + ' failed')
                    assert False
                if ntp_verify_file_fuzzy(ntpc1, 'ntpkey_mvta_', self.vxprompt) is False:
                    log.error('generate ntpkey_mvta_' + ' failed')
                    assert False
                if ntp_verify_file_fuzzy(ntpc1, 'ntpkey_iffkey_') is False:
                    log.error('generate ntpkey_iffkey_' + ' failed')
                    assert False

                # export GQpar, MVpar, IFFpar
                ntpc1.sendAndExpect('ntpkey -r rnd -e -p 12345678', self.vxprompt)

                ntpc2.send('tftp ' + ntps_ip + ' get rnd')
                ntpc2.expect('Transfer completed:')
                if ntp_verify_file(ntpc2, 'rnd', self.vxprompt) is False:
                    log.error('Randfile rnd is not existed.')
                    assert False
                # change z hostname
                ntpc2.sendAndExpect('ntpkey -Z ntpclient', self.vxprompt)
                # generate z hostkey and cert
                ntpc2.sendAndExpect('ntpkey -r rnd -H -p 12345678', self.vxprompt)
                time.sleep(10)
                if ntp_verify_file_fuzzy(ntpc2, 'ntpkey_cert_', self.vxprompt) is False:
                    log.error('generate ntpkey_cert_' + ' failed')
                    assert False
                if ntp_verify_file_fuzzy(ntpc2, 'ntpkey_host_', self.vxprompt) is False:
                    log.error('generate ntpkey_host_' + ' failed')
                    assert False

                # generate configure file ntp.conf, adding server info into it
                # target t will synchronize with linux target s
                ntps.sendAndExpect('cd ntp', self.lxprompt)
                ntps.sendAndExpect('cp ntp.conf ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo server ' + ntps_ip + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo keysdir ./' + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo statsdir ./' + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo logfile ntp.log ' + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo crypto pw 12345678 ' + '>> ntp.conf', self.lxprompt)
                ntps.sendAndExpect('echo crypto randfile rnd ' + '>> ntp.conf', self.lxprompt)

                # target z will synchronize with target t
                ntps.sendAndExpect('echo server ' + ntpc1_ip + ' autokey ' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo keysdir ./' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo statsdir ./' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo logfile ntp.log ' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo crypto pw 12345678 ' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo crypto randfile rnd ' + '>> ntp2.conf', self.lxprompt)
                ntps.sendAndExpect('echo enable auth ' + '>> ntp2.conf', self.lxprompt)

                # download ntp.conf to local
                ntpc1.send('tftp ' + ntps_ip + ' get ntp.conf')
                ntpc1.expect('Transfer completed:')
                if ntp_verify_file(ntpc1, 'ntp.conf', self.vxprompt) is False:
                    log.error('ntp.conf is not existed.')
                    assert False
                ntpc2.send('tftp ' + ntps_ip + ' get ntp2.conf')
                ntpc2.expect('Transfer completed:')
                if ntp_verify_file(ntpc2, 'ntp2.conf', self.vxprompt) is False:
                    log.error('ntp2.conf is not existed.')
                    assert False

                # set target t invalid time
                current_day, one_year_ago = get_dates_with_diff_year()
                this_year = current_day.split('-')[0]
                last_year = one_year_ago.split('-')[0]
                print('current_day=%s, one_year_ago=%s, last_yaer=%s, this_year=%s' % (
                current_day, one_year_ago, last_year, this_year))

                ntpc1.send("date %s" % one_year_ago)
                ntpc1.expect("ok", timeout=300)  # extra long timeout on first date command
                ntpc1.send("date")
                ntpc1.expect(last_year)
                # set target z invalid time
                ntpc2.send("date %s" % one_year_ago)
                ntpc2.expect("ok", timeout=300)  # extra long timeout on first date command
                ntpc2.send("date")
                ntpc2.expect(last_year)

                # start ntp daemon with configure file
                ntpc1.sendAndExpect('sysvar unset ipntp.config.param')
                ntpc2.sendAndExpect('sysvar unset ipntp.config.param')
                ntpc1.sendAndExpect('sysvar set -co ipntp.init.param "-c ntp.conf -g"', self.vxprompt)
                ntpc2.sendAndExpect('sysvar set -co ipntp.init.param "-c ntp2.conf -g"', self.vxprompt)
                ntpc1.sendAndExpect('ipd start ipntp', self.vxprompt)
                # waiting for t synchronize to the server about 10 minutes
                wait_cmd_ready(ntpc1, 'date', this_year, self.vxprompt)

                ntpc2.sendAndExpect('ipd start ipntp', self.vxprompt)
                # waiting for z synchronize to the autokey server t about 1 hour
                # at ubuntu 12.04, it can be done with 20 minutes
                # however at ubuntu 18.04, it cannot be done with 1 hours
                wait_cmd_ready(ntpc2, 'date', this_year, self.vxprompt, timeout=3600)

                # clean
                stop_ntpd(ntps, self.lxprompt)
                # delete local files ---xiaozhan  need debug the directory
                ntpc1.sendAndExpect('rm ntp.conf', self.vxprompt)
                ntpc1.sendAndExpect('rm ntp.log', self.vxprompt)
                ntpc1.sendAndExpect('rm rnd', self.vxprompt)
                ntpc1.sendAndExpect('rm ntpkey_cert_ntpserver', self.vxprompt)
                ntpc1.sendAndExpect('rm ntpkey_gqkey_ntpserver', self.vxprompt)
                ntpc1.sendAndExpect('rm ntpkey_host_ntpserver', self.vxprompt)
                ntpc1.sendAndExpect('rm ntpkey_iffkey_ntpserver', self.vxprompt)
                ntpc1.sendAndExpect('rm ntpkey_mvta_ntpserver', self.vxprompt)
                ntpc2.sendAndExpect('rm ntp2.conf', self.vxprompt)
                ntpc2.sendAndExpect('rm ntp.log', self.vxprompt)
                ntpc2.sendAndExpect('rm rnd', self.vxprompt)
                ntpc2.sendAndExpect('rm ntpkey_cert_ntpclient', self.vxprompt)
                ntpc2.sendAndExpect('rm ntpkey_host_ntpclient', self.vxprompt)
                ntpc1.sendAndExpect('ls', self.vxprompt)
                ntpc2.sendAndExpect('ls', self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_ipntp_debug(self, version):
        with allure.step('IPNTP debug control funcition test.'):
            ntpc = self.t1
            name = 'ipntp_debug'
            case_name = self.module + '.' + name + '-' + version
            try:
                # Because we should not start debug mode for other case ,so we
                # just test debug level set
                ntpc.send('sysvar get ipcom.syslogd.default_priority')
                ntpc.expect("sysvar: ipcom.syslogd.default_priority=2")
                ntpc.send('syslog list')
                ntpc.expect("ipntp.*?")
                ntpc.send('syslog priority ipntp DEBUG')
                ntpc.expect("syslog: facility ipntp priority set to DEBUG")
                ntpc.send('syslog list')
                ntpc.expect("ipntp.*?Debug")
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