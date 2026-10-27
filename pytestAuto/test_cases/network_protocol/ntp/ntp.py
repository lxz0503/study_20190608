#############################################################################
#
# Copyright (c) 2014, 2016, 2018, 2020-2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#

'NTP API'

import os
import config
import time
import util
import subprocess
import pexpect
import socket
import re

from datetime import date, datetime, timedelta

################################################################################
#        ntpq_send_and_return_all - ntpq cmd
################################################################################
def ntpq_send_and_return_all(ntpq, cmd, prompt = 'ntpq> ', append = ''):
    '''uses pexpect
    returns a list of all lines of output, stripped of crap like leading/trailing whitespace.'''
    ntpq.send(cmd.strip() + append)
    ntpq.expect(prompt)
    all = ntpq.s.s.before

    all = all.replace('\r\n\x00', '')

    lines0 = all.split('\r\n') #split lines. this is pty style newlines.
    lines0 = lines0[0:] # all but cmd
    if len(lines0) == 0:
        return []
    lines1 = []
    for a in lines0:
        a = a.strip()
        lines1.append(a) # strip leading / trailing whitespace
    while len(lines1) > 0 and lines1[0] == '': # remove any leading empty lines
        lines1 = lines1[1:]
    while len(lines1) > 0 and lines1[-1] == '': # remove any trailing empty lines
        lines1 = lines1[:-1]
    return lines1

################################################################################
#        ntpdc_send_and_return_all - ntpdc cmd
################################################################################
def ntpdc_send_and_return_all(ntpdc, cmd, prompt = 'ntpdc> ', append = ''):
    '''uses pexpect
    returns a list of all lines of output, stripped of crap like leading/trailing whitespace.'''
    ntpdc.send(cmd.strip() + append)
    ntpdc.expect(prompt)
    all = ntpdc.s.s.before

    all = all.replace('\r\n\x00', '')

    lines0 = all.split('\r\n') #split lines. this is pty style newlines.
    lines0 = lines0[0:] # all but cmd
    if len(lines0) == 0:
        return []
    lines1 = []
    for a in lines0:
        a = a.strip()
        lines1.append(a) # strip leading / trailing whitespace
    while len(lines1) > 0 and lines1[0] == '': # remove any leading empty lines
        lines1 = lines1[1:]
    while len(lines1) > 0 and lines1[-1] == '': # remove any trailing empty lines
        lines1 = lines1[:-1]
    return lines1

################################################################################
#        ntp_verify_response - verify ntpq and ntpdc response
################################################################################
def ntp_verify_response(lines, response, offset = 0):
    response = response[offset:]

    for i in range(len(lines)):
        line = lines[i]
        if len(line) == 0:
            continue
        if line.find(response) != -1:
                return True
    raise test_fail('Response mismatch ('  + line + ' != ' + response)

################################################################################
#        ntp_verify_response_return_assID - verify ntpq and ntpdc response and return assID
################################################################################
def ntp_verify_response_return_assID(lines, response, offset = 0):
    response = response[offset:]

    for i in range(len(lines)):
        line = lines[i]
        if len(line) == 0:
            continue
        if line.find(response) != -1:
            line = lines[i+2]
            item = line.split()
            return item[1]
    raise test_fail('Response mismatch ('  + line + ' != ' + response)

################################################################################
#        stop_ntpd - Stop Network Time Protocol Daemon
################################################################################
def stop_ntpd(s):
    s.send('pkill -9 ntpd')
    s.wait_prompt()

################################################################################
#        ntp_verify_file
################################################################################
def ntp_verify_file(t, filename):
    lines=t.send_and_return_all('ls')
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
def ntp_verify_file_fuzzy(t, fuzzy_filename):
    lines=t.send_and_return_all('ls')
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
    lines=t.send_and_return_all('ls')
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

def start_ntpd(s, v6, file):
    stop_ntpd(s)

    # try to set clock for 15 minutes then exit
    s.send('ntpd -q -c ~/ntp/' + file)
    s.wait_prompt(timeout = (15*60))
    s.send('ntpd -c ~/ntp/' + file)
    s.wait_prompt(timeout = 60)
    s.send('ps aux')
    s.expect_exact_and_wait_prompt('ntpd')
    
    # try synchronizing the ntp daemon for 5 minutes
    for count in range(5 * 60 / 5):
        s.send('ntpdate -p 1 -d ' + s.ip(v6).addr)
        i = s.expect_exact_and_wait_prompt(['no server suitable for synchronization found', 'adjust time server', 'step time server'])
        if i == 1 or i == 2:
            break
        time.sleep(5)
    else:
        raise test_fail('no server suitable for synchronization found')


################################################################################
#        copy_ntp_config - Copy ntp config files
################################################################################
def copy_ntp_config(s):
    ntpdir=os.path.join(config.productroot, config.productpath['ipntp'], 'test', 'ntp')
    try:
        s.ftp_transfer(ntpdir)
    except:
        s.scp_recursive_upload(ntpdir)


def wait_cmd_ready(host, cmd, expect_re, timeout=1200, interval=5):
    ptn = '(?s)' + expect_re
    start_time = time.time()
    i = 0
    
    while True:
        if (time.time() - start_time) >= timeout:
            raise test_fail('timeout after %s seconds' % timeout)
            break

        lines = host.send_and_return_all(cmd)
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
        one_year_ago = after_today(-(365+i))
        last_year = one_year_ago.split('-')[0]
        if this_year != last_year:
            break
    return current_day, one_year_ago

################################################################################
#        api - Test the IPNTP API
################################################################################
class api:
    '''IPNTP api'''

    def config(self):
        self.eta = 15
        self.hosts = 2
        self.require_types = ['ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        #self.will_fail = True

    def test(self, log, hosts, v6, __):
        filename = 'ntp.server.unicast.conf'
        t,s = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        copy_ntp_config(s)
        start_ntpd(s, v6, filename);

        t.ping(s.ip().addr, count = 2, retries = 5)
        t.send('ntp -v')
        t.expect_re_and_wait_prompt("All rights reserved.")
        t.send('ntp')
        t.expect_re_and_wait_prompt("     The ntp command will exit with 0 on success, and non-zero on errors.")
        t.send('ntp -u')
        t.expect_exact_and_wait_prompt("No ntp server specified!")
        t.send('ntp -t 20 -u ' + s.ip().addr)
        t.expect_re_and_wait_prompt("System time updated")
        t.send('ntp -t 20 -q ' + s.ip().addr)
        t.expect_re_and_wait_prompt("20[0-9][0-9]")


################################################################################
#        daemon - Test the IPNTP ntpd ntpq ntpdc daemon
################################################################################
class daemon_nokey:
    '''IPNTP ntpd ntpq ntpdc.

    This tests all the IPNTP daemons.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (broadcast enabled).
    3. Let ntp daemon sychronize with linux.
    4. Verify that system time is updated on target'''

    def config(self):
        self.eta = 22
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        self.v6 = False

    def test(self, log, hosts, v6, __):
        filename = 'ntp.server.unicast.conf'
        (t,z,s) = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        t.ping(z.ip().addr, count = 2, retries = 5)
        
        copy_ntp_config(s)
        start_ntpd(s, v6, filename);

        #stop ipntp
        t.stop_proc('ipntp');
        z.stop_proc('ipntp');

        #set peer invalid time
        t.send("date 1999-01-02")
        t.expect_exact_and_wait_prompt("ok", timeout = 300) # extra long timeout on first date command
        t.send("date")
        t.expect_re_and_wait_prompt("1999")
        
        #start ntp daemon with primary server
        #ntplog=os.path.join(config.productroot, config.productpath['ipntp'], 'test', 'ntp', 'ntp.log')
        t.set_sysvar('ipntp.config.param', "server %s; disable auth;logfile ntp.log" %(z.ip().addr))
        z.set_sysvar('ipntp.config.param', "server %s; disable auth;logfile ntp.log" %(s.ip().addr))
        t.set_sysvar('ipntp.init.param', "-g -A")
        z.set_sysvar('ipntp.init.param', "-g -A")

        #waiting for synchronizing to the server about 10 minutes
        z.start_proc('ipntp')
        #verify time
        wait_cmd_ready(z, 'date', '20[0-9][0-9]')
        
        #waiting for t synchronize to the z about 10 minutes
        t.start_proc('ipntp')
        #verify time
        wait_cmd_ready(z, 'date', '20[0-9][0-9]')
        #t.send_and_wait_prompt('cat ntp.log')
        #z.send_and_wait_prompt('cat ntp.log')
        
        #query state
        t.send('ntp -p')
        t.wait_prompt()
        #t.expect_re_and_wait_prompt("st t when poll reach   delay")
        t.send('ntp -d')
        t.wait_prompt()
        #t.expect_re_and_wait_prompt("st poll reach  delay   offset")

        #clean
        stop_ntpd(s)
        #delete local files
        t.send_and_wait_prompt('rm ntp.log');
        z.send_and_wait_prompt('rm ntp.log');
        t.send_and_wait_prompt('ls');
        z.send_and_wait_prompt('ls');



################################################################################
#        daemon_symkey - Test the IPNTP ntpd daemon with a symmetrical key
################################################################################
class daemon_symkey:
    '''IPNTP ntpd with a symmetrical key.

    This tests all the IPNTP daemons.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (broadcast enabled).
    3. Generate MD5 key, hostkey and cert in target t&z
    4. Let target t sychronize with linux.
    5. Let target z sychronize with target t using symmetrical key.
    6. Verify that system time is updated on target t&z'''

    def config(self):
        self.eta = 850
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        self.v6 = False

    def test(self, log, hosts, v6, __):
        filename = 'ntp.server.unicast.conf'
        (t,z,s) = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        t.ping(z.ip().addr, count = 2, retries = 5)
        
        copy_ntp_config(s)
        start_ntpd(s, v6, filename);

        #stop ipntp
        t.stop_proc('ipntp');
        z.stop_proc('ipntp');

        #set target t invalid time
        current_day, one_year_ago = get_dates_with_diff_year()
        this_year = current_day.split('-')[0]
        last_year = one_year_ago.split('-')[0]

        t.send("date %s" % one_year_ago)
        t.expect_exact_and_wait_prompt("ok", timeout = 300) # extra long timeout on first date command
        t.send("date")
        t.expect_re_and_wait_prompt(last_year)
        #set target z invalid time
        z.send("date %s" % one_year_ago)
        z.expect_exact_and_wait_prompt("ok", timeout = 300) # extra long timeout on first date command
        z.send("date")
        z.expect_re_and_wait_prompt(last_year)
        
        #copy rand file to target
        s.send_and_wait_prompt('pkill -9 in.tftpd')
        s.send_and_wait_prompt('in.tftpd --daemon ~/ntp/')
        s.send('ps aux')
        s.expect_exact_and_wait_prompt('in.tftpd')
        t.ping(s.ip().addr, count = 2, retries = 5)
        t.send_and_wait_prompt('tftp ' + s.ip().addr + ' get rnd')
        if ntp_verify_file(t, 'rnd') == False:
            raise test_fail('Randfile rnd is not existed.')

        #generate MD5 keys
        t.send_and_wait_prompt('ntpkey -r rnd -M -p password1 -S RSA -s hostname')
        time.sleep(10)
        if ntp_verify_file_fuzzy(t, 'ntp.keys') == False:
            raise test_fail('generate MD5 key' + ' failed')

        #using MD5 keyfile from linux
        t.send_and_wait_prompt('tftp ' + s.ip().addr + ' get ntpkeys')
        if ntp_verify_file(t, 'ntpkeys') == False:
            raise test_fail('ntpkeys is not existed.')
        z.send_and_wait_prompt('tftp ' + s.ip().addr + ' get ntpkeys')
        if ntp_verify_file(z, 'ntpkeys') == False:
            raise test_fail('ntpkeys is not existed.')
            
        z.send_and_wait_prompt('tftp ' + s.ip().addr + ' get rnd')
        if ntp_verify_file(z, 'rnd') == False:
            raise test_fail('Randfile rnd is not existed.')

        #generate configure file ntp.conf, adding server info into it
        #target s will synchronize with linux target
        s.sh.send('cd ntp', sudo = False)
        s.wait_prompt()
        s.sh.send('cp ntp.conf ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo server ' + s.ip().addr + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo driftfile drift' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo keys ntpkeys' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo statsdir ./' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo logfile ntp.log ' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo trustedkey 1 ' + '>> ntp.conf', sudo = False)
        s.wait_prompt()  
        
        #target z will synchronize with target s
        s.sh.send('echo server ' + t.ip().addr + ' key 1 ' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo keys ntpkeys' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo statsdir ./' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo logfile ntp.log ' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo trustedkey 1 ' + '>> ntp2.conf', sudo = False)
        s.wait_prompt() 

        #download ntp.conf to local
        t.send_and_wait_prompt('tftp ' + s.ip().addr + ' get ntp.conf')
        if ntp_verify_file(t, 'ntp.conf') == False:
            raise test_fail('ntp.conf is not existed.')
        z.send_and_wait_prompt('tftp ' + s.ip().addr + ' get ntp2.conf')
        if ntp_verify_file(z, 'ntp2.conf') == False:
            raise test_fail('ntp2.conf is not existed.')
        
        #start ntp daemon with configure file
        t.unset_sysvar('ipntp.config.param', cleanup = True)
        z.unset_sysvar('ipntp.config.param', cleanup = True)
        t.set_sysvar('ipntp.init.param', "-c ntp.conf -g")
        z.set_sysvar('ipntp.init.param', "-c ntp2.conf -g")
        t.start_proc('ipntp')
        #waiting for synchronizing to the server about 10 minutes
        #verify time
        wait_cmd_ready(t, 'date', this_year)
        t.send_and_wait_prompt('cat ntp.log')

        #change z hostname
        z.send_and_wait_prompt('ntpkey -Z ntpclient')
        z.start_proc('ipntp')
        #waiting for z synchronizing to the t about 1 hour
        # at ubuntu 12.04, it can be done with 20 minutes
        # however at ubuntu 18.04, it cannot be done with 1 hours
        wait_cmd_ready(z, 'date', this_year, timeout=3600)
        z.send_and_wait_prompt('cat ntp.log')

        #delete local files
        t.send_and_wait_prompt('rm ntp.conf')
        t.send_and_wait_prompt('rm ntp.log')
        t.send_and_wait_prompt('rm rnd')
        t.send_and_wait_prompt('rm ntpkeys')
        t.send_and_wait_prompt('rm ntp.keys')
        z.send_and_wait_prompt('rm ntp2.conf')
        z.send_and_wait_prompt('rm ntp.log')
        z.send_and_wait_prompt('rm rnd')
        z.send_and_wait_prompt('rm ntpkeys')
        z.send_and_wait_prompt('rm ntpkey_cert_ntpclient')
        z.send_and_wait_prompt('rm ntpkey_host_ntpclient')
        t.send_and_wait_prompt('ls');
        z.send_and_wait_prompt('ls');
        
        #clean
        stop_ntpd(s)



################################################################################
#        daemon_autokey - Test the IPNTP ntpd daemon with autokey
################################################################################
class daemon_autokey:
    '''IPNTP ntpd with autokey(GQ and MV scheme).

    This tests all the IPNTP daemons.
    1. Set incorrect system time on target.
    2. Start Linux ntpd (broadcast enabled).
    3. Generate GQ&MV key, hostkey and cert in target t with pass 12345678
    4. Generate hostkey and cert in target z with same pass 12345678
    5. Get GQ&MV key from target t.
    6. Set incorrect time in target t and z.
    7. Let target t sychronize with linux.
    8. Let target z sychronize with target t using autokey.
    9. Verify that system time is updated on target t&z'''

    def config(self):
        self.eta = 850
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux']
        self.works_on_lkm = True
        self.works_on_iplite = True
        self.v6 = False

    def test(self, log, hosts, v6, __):
        filename = 'ntp.server.unicast.conf'
        (t,z,s) = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        t.ping(z.ip().addr, count = 2, retries = 5)
        
        copy_ntp_config(s)
        start_ntpd(s, v6, filename);

        #stop ipntp
        t.stop_proc('ipntp');
        z.stop_proc('ipntp');
        
        #Firstly set t and z to correct time. This latest time
        #will be used to generate certificate for the certficate will
        #be expired in one year.
        t.send('ntp -t 20 -u ' + s.ip().addr)
        t.expect_re_and_wait_prompt("System time updated")
        z.send('ntp -t 20 -u ' + s.ip().addr)
        z.expect_re_and_wait_prompt("System time updated")
        
        #copy rand file to target
        s.send_and_wait_prompt('pkill -9 in.tftpd')
        s.send_and_wait_prompt('in.tftpd --daemon ~/ntp/')
        s.send('ps aux')
        s.expect_exact_and_wait_prompt('in.tftpd')
        t.ping(s.ip().addr, count = 2, retries = 5)
        t.send_and_wait_prompt('tftp ' + s.ip().addr + ' get rnd')
        if ntp_verify_file(t, 'rnd') == False:
            raise test_fail('Randfile rnd is not existed.')
        #change t hostname
        t.send_and_wait_prompt('ntpkey -Z ntpserver')
        #generate GQkey, MVkey, IFFkey, hostkey and trust cert
        t.send_and_wait_prompt('ntpkey -r rnd -T -G -V 5 -I -p 12345678')
        time.sleep(10)
        if ntp_verify_file_fuzzy(t, 'ntpkey_cert_') == False:
            raise test_fail('generate ntpkey_cert_' + ' failed')
        if ntp_verify_file_fuzzy(t, 'ntpkey_host_') == False:
            raise test_fail('generate ntpkey_host_' + ' failed')
        if ntp_verify_file_fuzzy(t, 'ntpkey_gqkey_') == False:
            raise test_fail('generate ntpkey_gqkey_' + ' failed')
        if ntp_verify_file_fuzzy(t, 'ntpkey_mvta_') == False:
            raise test_fail('generate ntpkey_mvta_' + ' failed')
        if ntp_verify_file_fuzzy(t, 'ntpkey_iffkey_') == False:
            raise test_fail('generate ntpkey_iffkey_' + ' failed')
        
        #export GQpar, MVpar, IFFpar
        t.send_and_wait_prompt('ntpkey -r rnd -e -p 12345678')
            
        z.send_and_wait_prompt('tftp ' + s.ip().addr + ' get rnd')
        if ntp_verify_file(z, 'rnd') == False:
            raise test_fail('Randfile rnd is not existed.')
        #change z hostname
        z.send_and_wait_prompt('ntpkey -Z ntpclient')
        #generate z hostkey and cert
        z.send_and_wait_prompt('ntpkey -r rnd -H -p 12345678')
        time.sleep(10)
        if ntp_verify_file_fuzzy(z, 'ntpkey_cert_') == False:
            raise test_fail('generate ntpkey_cert_' + ' failed')
        if ntp_verify_file_fuzzy(z, 'ntpkey_host_') == False:
            raise test_fail('generate ntpkey_host_' + ' failed')

        #generate configure file ntp.conf, adding server info into it
        #target t will synchronize with linux target s
        s.sh.send('cd ntp', sudo = False)
        s.wait_prompt()
        s.sh.send('cp ntp.conf ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo server ' + s.ip().addr + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo keysdir ./' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo statsdir ./' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo logfile ntp.log ' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo crypto pw 12345678 ' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo crypto randfile rnd ' + '>> ntp.conf', sudo = False)
        s.wait_prompt()
        
        #target z will synchronize with target t
        s.sh.send('echo server ' + t.ip().addr + ' autokey ' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo keysdir ./' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo statsdir ./' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo logfile ntp.log ' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo crypto pw 12345678 ' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo crypto randfile rnd ' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        s.sh.send('echo enable auth ' + '>> ntp2.conf', sudo = False)
        s.wait_prompt()
        
        #download ntp.conf to local
        t.send_and_wait_prompt('tftp ' + s.ip().addr + ' get ntp.conf')
        if ntp_verify_file(t, 'ntp.conf') == False:
            raise test_fail('ntp.conf is not existed.')
        z.send_and_wait_prompt('tftp ' + s.ip().addr + ' get ntp2.conf')
        if ntp_verify_file(z, 'ntp2.conf') == False:
            raise test_fail('ntp2.conf is not existed.')
        
        #get gq key from target t
        #tftpsdir = t.send_and_return_all('pwd')
        #t.stop_proc('iptftps')
        #t.set_sysvar('iptftp.dir', tftpsdir[0])
        #t.start_proc('iptftps')
        #tname = ntp_gethostname_from_file(t, 'ntpkey_host_')
        #if len(tname) == 0:
        #    raise test_fail('Get target t hostname failed.')
        #z.send_and_wait_prompt('tftp ' + t.ip().addr + ' get ntpkey_gq_' + tname)
        #if ntp_verify_file(z, 'ntpkey_gq_' + tname) == False:
        #    raise test_fail('Get gqkey file failed.')
        
        #get mv key1 from target t
        #mvkeyname = ntp_gethostname_from_file(t, 'ntpkey_MVkey1_')
        #if len(mvkeyname) == 0:
        #    raise test_fail('Get target t MVkey1 failed.')
        #rename ntpkey_MVkey1_iptarget.xxxx to ntpkey_mv_iptarget
        #z.send_and_wait_prompt('tftp ' + t.ip().addr + ' get ntpkey_MVkey1_' + mvkeyname + ' ntpkey_mv_' + tname)
        #if ntp_verify_file(z, 'ntpkey_mv_' + tname) == False:
        #    raise test_fail('Get ntpkey_mv_ file failed.')
        
        #set target t invalid time
        current_day, one_year_ago = get_dates_with_diff_year()
        this_year = current_day.split('-')[0]
        last_year = one_year_ago.split('-')[0]
        print('current_day=%s, one_year_ago=%s, last_yaer=%s, this_year=%s' % (current_day, one_year_ago, last_year, this_year))

        t.send("date %s" % one_year_ago)
        t.expect_exact_and_wait_prompt("ok", timeout = 300) # extra long timeout on first date command
        t.send("date")
        t.expect_re_and_wait_prompt(last_year)
        #set target z invalid time
        z.send("date %s" % one_year_ago)
        z.expect_exact_and_wait_prompt("ok", timeout = 300) # extra long timeout on first date command
        z.send("date")
        z.expect_re_and_wait_prompt(last_year)
        
        #z.send_and_wait_prompt('cat ntp2.conf')

        #start ntp daemon with configure file
        t.unset_sysvar('ipntp.config.param', cleanup = True)
        z.unset_sysvar('ipntp.config.param', cleanup = True)
        t.set_sysvar('ipntp.init.param', "-c ntp.conf -g")
        z.set_sysvar('ipntp.init.param', "-c ntp2.conf -g")
        t.start_proc('ipntp')
        #waiting for t synchronize to the server about 10 minutes
        wait_cmd_ready(t, 'date', this_year)
        
        z.start_proc('ipntp')
        #waiting for z synchronize to the autokey server t about 1 hour
        # at ubuntu 12.04, it can be done with 20 minutes
        # however at ubuntu 18.04, it cannot be done with 1 hours
        wait_cmd_ready(z, 'date', this_year, timeout=3600)
       
        #clean
        stop_ntpd(s)
        #delete local files
        t.send_and_wait_prompt('rm ntp.conf')
        t.send_and_wait_prompt('rm ntp.log')
        t.send_and_wait_prompt('rm rnd')
        t.send_and_wait_prompt('rm ntpkey_cert_ntpserver')
        t.send_and_wait_prompt('rm ntpkey_gqkey_ntpserver')
        t.send_and_wait_prompt('rm ntpkey_host_ntpserver')
        t.send_and_wait_prompt('rm ntpkey_iffkey_ntpserver')
        t.send_and_wait_prompt('rm ntpkey_mvta_ntpserver')
        z.send_and_wait_prompt('rm ntp2.conf')
        z.send_and_wait_prompt('rm ntp.log')
        z.send_and_wait_prompt('rm rnd')
        z.send_and_wait_prompt('rm ntpkey_cert_ntpclient')
        z.send_and_wait_prompt('rm ntpkey_host_ntpclient')
        t.send_and_wait_prompt('ls');
        z.send_and_wait_prompt('ls');

class ipntp_debug:
    'IPNTP debug control funcition test.'

    def config(self):
        self.eta = 10
        self.hosts = 1
        self.works_on_lkm = False
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        nut = hosts
           
        #Because we should not start debug mode for other case ,so we 
		# just test debug level set
        nut.send('sysvar get ipcom.syslogd.default_priority')
        nut.expect_re_and_wait_prompt("sysvar: ipcom.syslogd.default_priority=2")
        nut.send('syslog list')
        nut.expect_re_and_wait_prompt("ipntp.*?")
        nut.send('syslog priority ipntp DEBUG')
        nut.expect_re_and_wait_prompt("syslog: facility ipntp priority set to DEBUG")
        nut.send('syslog list')
        nut.expect_re_and_wait_prompt("ipntp.*?Debug")
		
