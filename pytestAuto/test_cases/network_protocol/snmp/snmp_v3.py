#############################################################################
#
# Copyright (c) 2018-2019, 2021-2022 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

"SNMP version 3 kong tests"

import os
import config
import subprocess
import socket
import re
import time
import util
from pexpect import TIMEOUT

#SNMP configurations cert and key files
snmp_key_files = ['cacert.pem',
                 'cert.sh',
                 'id_rsa',
                 'id_rsa.pub',
                 'openssl.cnf',
                 'revo.pk2',
                 'root.pem',
                 'root.sh',
                 'root.srl',
                 'rootkey.pem',
                 'rootreq.pem',
                 'snmpca.crt',
                 'snmpclient.crt',
                 'snmpclient.key',
                 'snmpclient.pem',
                 'snmpclientcert.pem',
                 'snmpclientkey.pem',
                 'snmpclientreq.pem',
                 'snmpserver.crt',
                 'snmpserver.key',
                 'snmpserver.pem',
                 'snmpservercert.pem',
                 'snmpserverkey.pem',
                 'snmpserverreq.pem']


################################################################################
#        snmp_expect_exact - expect string and quit if not match
################################################################################
def snmp_expect_exact(client, expect_results):
    '''uses expect_exact to compare the results, quit snmptalk if not match'''
    try:
        client.expect_exact(expect_results)
    except TIMEOUT:
        # cleanup 
        client.send("quit")
        raise test_fail("snmp_expect_exact failed to match %s " % expect_results)
        
################################################################################
#        copy_snmp_config - Copy snmp config files
################################################################################
def copy_snmp_config(s):
    snmpdir=os.path.join(config.productroot, config.productpath['snmp'], 'test', 'conf')
    try:
        s.ftp_transfer(snmpdir)
    except:
        s.scp_recursive_upload(snmpdir)


################################################################################
#        snmp_verify_file
################################################################################
def snmp_verify_file(t, filename):
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
#        download_snmp_certkey_files
################################################################################
def download_snmp_certkey_files(target, keydir, key_files):
    # Put all necessary cert or key files on the target
    import ftplib
    ftp = ftplib.FTP(target.login_ip().addr)
    ftp.login('ftp', 'interpeak')

    for fn in snmp_key_files:
        data = open(keydir + "/" + fn)
        ftp.storbinary('STOR %s' % os.path.basename(fn), data)
        data.close()
    ftp.quit()

        
################################################################################
class snmp_v3_udp_noAuthNoPriv:
    'snmp version 3 udp transport test'
    def config(self):
        self.eta = 20
        self.hosts = 2
        self.prompt = "snmptalk"
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 161")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("version 3 UDP initialmd5 noAuthNoPriv")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:UDP")
        c.send("status")
        c.expect_exact("tos:noAuthNoPriv, user name:initialmd5")
        c.send("status")
        c.expect_exact("at port 161")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String")
        #should failed for setting is not allowed in noAuthNopriv
        c.send("set sysName.0 interpeak")
        snmp_expect_exact(c, "SNMP agent reports `authorization error'")
        c.send("next sysName.0")
        snmp_expect_exact(c, "sysLocation.0    	String")
        c.send("walk")
        time.sleep(120)
        snmp_expect_exact(c, "No more in MIB")
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")
        
        
class snmp_v3_udp_authNoPriv:
    'snmp version 3 udp transport authNoPriv test'
    def config(self):
        self.eta = 20
        self.hosts = 2
        self.prompt = "snmptalk"
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 161")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("version 3 UDP initialmd5 authNoPriv md5 initialmd5")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:UDP")
        c.send("status")
        c.expect_exact("tos:authNoPriv, user name:initialmd5")
        c.send("status")
        c.expect_exact("at port 161")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String")
        c.send("set sysName.0 interpeak")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        
        #use sha
        c.send("version 3 UDP initialsha authNoPriv sha initialsha")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("tos:authNoPriv, user name:initialsha")
        c.send("next sysName.0")
        snmp_expect_exact(c, "sysLocation.0    	String")
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")
        
        
class snmp_v3_udp_authPriv:
    'snmp version 3 udp transport authPriv test'
    def config(self):
        self.eta = 20
        self.hosts = 2
        self.prompt = "snmptalk"
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 161")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("version 3 UDP initialmd5  authPriv md5 initialmd5 des initialmd5")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:UDP")
        c.send("status")
        c.expect_exact("tos:authPriv, user name:initialmd5")
        c.send("status")
        c.expect_exact("at port 161")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String")
        c.send("set sysName.0 interpeak")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        
        #use sha
        ''' Not supported AES in snmptalk yet
        c.send("version 3 UDP initialsha authPriv sha initialsha aes initialsha")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("tos:authPriv, user name:initialsha")
        c.send("next sysName.0")
        snmp_expect_exact(c, "sysLocation.0    	String")'''
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")
        
        
class snmp_v3_SSH_user_by_pass:
    'snmp version 3 ssh transport authPriv test with username and password'
    def config(self):
        self.eta = 20
        self.hosts = 2
        self.prompt = "snmptalk"
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        
        #start server SSH task
        s.start_proc('ipssh')
        time.sleep(1)
        
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 22")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("version 3 SSH")
        c.expect_exact(self.prompt)
        c.send("ssh_user ftp interpeak")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:SSH")
        c.send("status")
        c.expect_exact("at port 22")
        c.send("status")
        c.expect_exact("ssh user name:ftp")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String")
        c.send("set sysName.0 interpeak")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")
        
        s.stop_proc('ipssh')
        
class snmp_v3_SSH_user_keyfile:
    'snmp version 3 ssh transport authPriv test with ssh key file'
    def config(self):
        self.eta = 22
        self.hosts = 2
        self.require_types = ['ipnet', 'ipnet']
        self.prompt = "snmptalk"
        self.v6 = False
        self.username = "revo"
        self.keyfilepass = "123456"

    def test(self, log, hosts, v6, _):
        c, s = hosts
        
        #start server SSH task
        s.start_proc('ipssh')
        time.sleep(1)
        
        #copy snmp config files to targets
        keydir = os.path.join(config.productroot, config.productpath['snmp'], 'test', 'conf')
        download_snmp_certkey_files(c, keydir, snmp_key_files)
        download_snmp_certkey_files(s, keydir, snmp_key_files)
        
        #verify is revo.pk2 exist in SSH server's SEC_VAULT_FILE_ROOT("/ram")?
        if snmp_verify_file(s, '%s.pk2' % self.username) == False:
            raise test_fail('pk2 file is not existed.')
        
        #verify is RSA key file exist in SNMP client?
        if snmp_verify_file(c, 'id_rsa') == False:
            raise test_fail('id_rsa file is not existed.')
        
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 22")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("version 3 SSH")
        c.expect_exact(self.prompt)
        c.send("ssh_user %s 123456" % self.username)
        c.expect_exact(self.prompt)
        c.send("ssh_key /ram/id_rsa")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:SSH")
        c.send("status")
        c.expect_exact("at port 22")
        c.send("status")
        c.expect_exact("ssh user name:%s" % self.username)
        c.send("status")
        c.expect_exact("ssh key file:/ram/id_rsa")
        c.send("get sysName.0")
        snmp_expect_exact(c, "Enter PEM pass phrase:")
        c.send("%s" % self.keyfilepass)
        snmp_expect_exact(c, "sysName.0    	String")
        
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")
        
        s.stop_proc('ipssh')
        
        
class snmp_v3_TLS_DTLS:
    'snmp version 3 TLS/DTLS transport authPriv test with cert/key file'
    def config(self):
        self.eta = 22
        self.hosts = 2
        self.require_types = ['ipnet', 'ipnet']
        self.prompt = "snmptalk"
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        
        #copy snmp config files to targets
        keydir = os.path.join(config.productroot, config.productpath['snmp'], 'test', 'conf')
        download_snmp_certkey_files(c, keydir, snmp_key_files)
        download_snmp_certkey_files(s, keydir, snmp_key_files)
        
        #import snmpserver key and restart SNMP TLS transport
        s.send_and_return_all("keydb import key snmpserver /ram/snmpserver.key")
        s.send("keydb import key snmpserver /ram/snmpserver.key")
        try:
            s.expect_exact("Failed: already installed")
        except TIMEOUT:
            raise test_fail("Failed: /ram/snmpserver.key is not installed")
        #Restart SNMP TLS/DTLS transport.
        s.send_and_return_all("C snmp_tls_restart")
        #time.sleep(1)
        #comment out this line for we may get a blank line at first and
        #then we will get another "Successfully to restart SNMP TLS model" line.
        #s.expect_exact("Successfully to restart SNMP TLS model")
        
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 10161")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("version 3 TLS")
        c.expect_exact(self.prompt)
        c.send("tls_localcert /ram/snmpclient.crt")
        c.expect_exact(self.prompt)
        c.send("tls_localkey /ram/snmpclient.key")
        c.expect_exact(self.prompt)
        c.send("tls_peercert /ram/snmpserver.crt")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:TLS")
        c.send("status")
        c.expect_exact("at port 10161")
        c.send("status")
        c.expect_exact("peer cert file:/ram/snmpserver.crt")
        c.send("status")
        c.expect_exact("local cert file:/ram/snmpclient.crt")
        c.send("status")
        c.expect_exact("local key file:/ram/snmpclient.key")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String")
        c.send("set sysName.0 interpeak")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        
        #run DTLS tests
        c.send("version 3 DTLS")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:DTLS")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        c.send("set sysName.0 dtlsserver")
        snmp_expect_exact(c, "sysName.0    	String(10): dtlsserver")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(10): dtlsserver")
        
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")

class snmp_v3_peerId_probe_usm:
    'snmp version 3 peerId probe test in USM'
    def config(self):
        self.eta = 20
        self.hosts = 2
        self.prompt = "snmptalk"
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("sec_id x 0000000c000000007f000002")
        c.send("status")
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 161")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("version 3 UDP initialmd5  authPriv md5 initialmd5 des initialmd5")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:UDP")
        c.send("status")
        c.expect_exact("tos:authPriv, user name:initialmd5")
        c.send("status")
        c.expect_exact("at port 161")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String")
        c.send("status")
        c.send("set sysName.0 interpeak")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        
        #use sha
        ''' Not supported AES in snmptalk yet
        c.send("version 3 UDP initialsha authPriv sha initialsha aes initialsha")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("tos:authPriv, user name:initialsha")
        c.send("next sysName.0")
        snmp_expect_exact(c, "sysLocation.0    	String")'''
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")
		
class snmp_v3_peerId_probe_tsm:
    'snmp version 3 peerId probe in TSM'
    def config(self):
        self.eta = 22
        self.hosts = 2
        self.require_types = ['ipnet', 'ipnet']
        self.prompt = "snmptalk"
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        
        #copy snmp config files to targets
        keydir = os.path.join(config.productroot, config.productpath['snmp'], 'test', 'conf')
        download_snmp_certkey_files(c, keydir, snmp_key_files)
        download_snmp_certkey_files(s, keydir, snmp_key_files)
        
        #import snmpserver key and restart SNMP TLS transport
        s.send_and_return_all("keydb import key snmpserver /ram/snmpserver.key")
        s.send("keydb import key snmpserver /ram/snmpserver.key")
        try:
            s.expect_exact("Failed: already installed")
        except TIMEOUT:
            raise test_fail("Failed: /ram/snmpserver.key is not installed")
        #Restart SNMP TLS/DTLS transport.
        s.send_and_return_all("C snmp_tls_restart")
        #time.sleep(1)
        #comment out this line for we may get a blank line at first and
        #then we will get another "Successfully to restart SNMP TLS model" line.
        #s.expect_exact("Successfully to restart SNMP TLS model")
        
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("con_id x 0000000c000000007f000002")
        c.send("status")		
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 10161")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("version 3 TLS")
        c.expect_exact(self.prompt)
        c.send("tls_localcert /ram/snmpclient.crt")
        c.expect_exact(self.prompt)
        c.send("tls_localkey /ram/snmpclient.key")
        c.expect_exact(self.prompt)
        c.send("tls_peercert /ram/snmpserver.crt")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:TLS")
        c.send("status")
        c.expect_exact("at port 10161")
        c.send("status")
        c.expect_exact("peer cert file:/ram/snmpserver.crt")
        c.send("status")
        c.expect_exact("local cert file:/ram/snmpclient.crt")
        c.send("status")
        c.expect_exact("local key file:/ram/snmpclient.key")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String")
        c.send("status")		
        c.send("set sysName.0 interpeak")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        
        #run DTLS tests
        c.send("version 3 DTLS")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:3 transport mode:DTLS")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(9): interpeak")
        c.send("set sysName.0 dtlsserver")
        snmp_expect_exact(c, "sysName.0    	String(10): dtlsserver")
        c.send("get sysName.0")
        snmp_expect_exact(c, "sysName.0    	String(10): dtlsserver")
        
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")

class snmp_mibway_access:
    'snmp mibway access through internal request test'
    def config(self):
        self.eta = 20
        self.hosts = 2
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        c.send("C webcliShellCmdInit()")
        c.expect_re_and_wait_prompt("value = 0 = 0x0")
        #c.send("webcli")
        c.send("webcli")
        c.expect_re("Login:")
        c.send("admin")
        c.expect_re("Password:")
        c.send("admin")
        c.send('wmset sysName "Wind River"')
        c.expect_exact("sysName = Wind River")
        c.send("wmget sysName")
        c.expect_exact("sysName = Wind River")
        c.send("logout")
        c.wait_prompt()
