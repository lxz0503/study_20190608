###########################################################################
#                       DESCRIPTION
###########################################################################

###########################################################################
#                       CONFIGURATION
###########################################################################

#TODO: test our tftps from a linux client

# This test verifies the functionality of the IPTFTP client and server

## REQUIRES THAT THE LINUX TARGET HAS in.tftpd (atftpd) SOMEWHERE
## IN THE PATH
## and an ftp server on the linux machine

###########################################################################
# Imports
###########################################################################
from iptestengine import test_fail
import config
import os
import re
import subprocess

###########################################################################
# Functions
###########################################################################

#==========================================================================
# verify_existence
#==========================================================================
def verify_existence(lines, file_name):
    'Verify existence of file "filename"'
    for i in range(len(lines)):
        line = lines[i]
        files = str.split(line)
        for j in range(len(files)):
            if os.path.basename(files[j]).lower() == file_name:
                return True
    else:
        return False

###########################################################################
# Test classes
###########################################################################

###########################################################################
## tftp_linux_is_server
###########################################################################
class tftp_linux_is_server:
    'TFTP client and server (ipnet client)'

    def config(self):
        self.hosts = 3
        self.require_types = [ 'ipnet', 'ipnet', 'linux' ]
        self.eta = 6
        self.v6  = False # ATFTPD doesnt support v6 yet.

    def test(self, log, hosts, v6, _):
        'TFTP client and server'
        (a, b, linux) = hosts
        #servers = ('192.168.200.254',)  #change
        tftp_dir = '~/tftpboot'

        #enabled allow.upload
        a.set_sysvar('iptftps.allow.upload', 'enable')
        b.set_sysvar('iptftps.allow.upload', 'enable')

        # Create the TFTP entries
        linux.send_and_wait_prompt('rm -rf ~/tftpboot')
        linux.send_and_wait_prompt('rm -rf ~/tftpcomp')
        linux.send_and_wait_prompt('mkdir ~/tftpcomp')
        linux.send_and_wait_prompt('chmod 777 ~/tftpcomp')

        #file_names = ('tftp0.txt', 'tftp1.txt', 'tftp2.txt', 'tftp0.bin', 'tftp1.bin', 'tftp2.bin')
        test_dir = os.path.join(config.productroot, config.productpath['iptftp'], 'test') + '/tftpboot'
        linux.ftp_transfer(test_dir, '~/tftpcomp')
        lnames = linux.ftp_transfer(test_dir)
        linux.send_and_wait_prompt('chmod 777 ~/tftpboot')
        linux.send_and_wait_prompt('pkill in.tftpd')
        linux.send_and_wait_prompt('in.tftpd --daemon ~/tftpboot/')

        file_names = []
        for file_name in lnames:
            # Only do level 1.
            file_name = file_name[len(test_dir):]
            file_name = file_name.strip('/')
            # Skip any subdirectories
            if len(os.path.split(file_name)[0]):
                continue
            file_names.append(os.path.basename(file_name))

        # Make sure no tftp test files are present on the target a
        for file_name in file_names:
            lines = a.send_and_return_all('rm ' + file_name)
            lines = a.send_and_return_all('ls')
            if verify_existence(lines, file_name) == True:
                raise test_fail('File %s not deleted' % (file_name))

        # Retrieve files from 'server'
        for file_name in file_names:
            a.send('tftp ' + linux.ip(v6).addr + ' get ' + file_name)
            a.expect_exact_and_wait_prompt('Transfer completed:')
            lines = a.send_and_return_all('ls')
            if verify_existence(lines, file_name) == False:
                raise test_fail('File %s not found' % (file_name))

        # Make sure no tftp test files are present on the target b
        for file_name in file_names:
            lines = b.send_and_return_all('cd tftpdir')
            lines = b.send_and_return_all('rm ' + file_name)
            lines = b.send_and_return_all('cd ..')
            lines = b.send_and_return_all('ls tftpdir')
            if verify_existence(lines, file_name) == True:
                raise test_fail('File %s not deleted' % (file_name))

        # Copy files from 'a' to 'b'
        for file_name in file_names:
            a.send('tftp ' + b.ip(v6).addr + ' put ' + file_name)
            a.expect_exact_and_wait_prompt('Transfer completed:')
            lines = b.send_and_return_all('ls tftpdir')
            if verify_existence(lines, file_name) == False:
                raise test_fail('File %s not found' % (file_name))

        # Copy files from 'b' to 'server'
        for file_name in file_names:
            lines = b.send_and_return_all('cd tftpdir')
            b.send('tftp ' + linux.ip(v6).addr + ' put ' + file_name + ' ' + file_name + '.copy')
            b.expect_exact_and_wait_prompt('Transfer completed:')
            lines = b.send_and_return_all('cd ..')
            linux.expect_prompt('cmp ~/tftpboot/%s.copy ~/tftpcomp/tftpboot/%s' % (file_name, file_name))


###########################################################################
## tftp_ipnet_is_server
###########################################################################
class tftp_ipnet_is_server:
    'TFTP client and server (ipnet server)'

    def config(self):
        self.hosts = 3
        self.require_types = ['ipnet', 'ipnet', 'linux' ]
        self.eta = 6
        self.v6  = False # ATFTPD doesnt support v6 yet.

    def test(self, log, hosts, v6, _):
        'TFTP client and server'
        (a, b, linux) = hosts
        tftp_dir = '~/tftpboot'

        #enabled allow.upload
        a.set_sysvar('iptftps.allow.upload', 'enable')
        b.set_sysvar('iptftps.allow.upload', 'enable')

        # Create the TFTP entries
        linux.send_and_wait_prompt('rm -rf ~/tftpboot')
        linux.send_and_wait_prompt('rm -rf ~/tftpcomp')
        linux.send_and_wait_prompt('mkdir ~/tftpcomp')
        linux.send_and_wait_prompt('chmod 777 ~/tftpcomp')

        #file_names = ('tftp0.txt', 'tftp1.txt', 'tftp2.txt', 'tftp0.bin', 'tftp1.bin', 'tftp2.bin')
        test_dir = os.path.join(config.productroot, config.productpath['iptftp'], 'test') + '/tftpboot'
        linux.ftp_transfer(test_dir, '~/tftpcomp')
        lnames = linux.ftp_transfer(test_dir)
        linux.send_and_wait_prompt('chmod 777 ~/tftpboot')
        linux.send_and_wait_prompt('pkill in.tftpd')
        linux.send_and_wait_prompt('in.tftpd --daemon ~/tftpboot/')

        file_names = []
        for file_name in lnames:
            # Only do level 1.
            file_name = file_name[len(test_dir):]
            file_name = file_name.strip('/')
            # Skip any subdirectories
            if len(os.path.split(file_name)[0]):
                continue
            file_names.append(os.path.basename(file_name))

        # Make sure no tftp test files are present on the target a
        for file_name in file_names:
            lines = a.send_and_return_all('cd tftpdir')
            lines = a.send_and_return_all('rm ' + file_name)
            lines = a.send_and_return_all('ls')
            if verify_existence(lines, file_name) == True:
                raise test_fail('File %s not deleted' % (file_name))
            lines = a.send_and_return_all('cd ..')

        # Send files from linux to ipnet tftp server
        for file_name in file_names:
            linux.send('atftp --trace -p -r %s -l ~/tftpboot/%s %s' % (file_name, file_name, a.ip(v6).addr))
            linux.expect_exact_and_wait_prompt('received ACK')
            lines = a.send_and_return_all('ls tftpdir')
            if verify_existence(lines, file_name) == False:
                raise test_fail('File %s not found' % (file_name))

        # Make sure no tftp test files are present on the target b
        for file_name in file_names:
            lines = b.send_and_return_all('cd tftpdir')
            lines = b.send_and_return_all('rm ' + file_name)
            lines = b.send_and_return_all('cd ..')
            lines = b.send_and_return_all('ls tftpdir')
            if verify_existence(lines, file_name) == True:
                raise test_fail('File %s not deleted' % (file_name))

        # Copy files from 'a' to 'b'
        for file_name in file_names:
            lines = a.send_and_return_all('cd tftpdir')
            a.send('tftp ' + b.ip(v6).addr + ' put ' + file_name)
            a.expect_exact_and_wait_prompt('Transfer completed:')
            lines = a.send_and_return_all('cd ..')
            lines = b.send_and_return_all('ls tftpdir')
            if verify_existence(lines, file_name) == False:
                raise test_fail('File %s not found' % (file_name))

        # Copy files from 'b' to 'server'
        for file_name in file_names:
            linux.send('atftp --trace -g -r %s -l %s %s' % (file_name, file_name + '.copy', b.ip(v6).addr))
            linux.expect_exact_and_wait_prompt('sent ACK')
            # Using md5sum to replace cmp, due to cmp command easy to be added with abnormal characters
            #linux.expect_prompt('cmp %s.copy ~/tftpcomp/tftpboot/%s' % (file_name, file_name))
            md5sum1 = '\n'.join(linux.send_and_return_all('md5sum %s.copy' % file_name)).split(' ')[0]
            md5sum2 = '\n'.join(linux.send_and_return_all('md5sum  ~/tftpcomp/tftpboot/%s' % file_name)).split(' ')[0]
            if md5sum1 != md5sum2:
                raise test_fail('%s tftped not matched original' % file_name)

###########################################################################
## tftp_no_server
###########################################################################
class tftp_no_server:
    'TFTP client without server'

    def config(self):
        self.hosts = 1
        self.require_types = [ 'ipnet' ]
        self.eta = 6

    def test(self, log, hosts, v6, _):
        'TFTP client without server'
        a = hosts
        tftp_dir = '~/tftpboot'

        lines = a.send_and_return_all('tftp')
        a.send('tftp -a noserver.interpeak.se get no_server.txt')
        a.expect_re_and_wait_prompt("Unknown host: noserver.interpeak.se")

###########################################################################
## tftp_ipv6_self_is_server
###########################################################################
class tftp_ipv6_self_is_server:
    'TFTP client and TFTP server (ipnet client)'

    def config(self):
        self.hosts = 2
        self.require_types = [ 'ipnet', 'ipnet' ]
        self.eta = 6
        self.v4  = False

    def test(self, log, hosts, v6, _):
        'TFTP client and TFTP server'
        (a, b) = hosts
        file_name = 'create.txt'

        #enabled allow.upload
        a.set_sysvar('iptftps.allow.upload', 'enable')
        b.set_sysvar('iptftps.allow.upload', 'enable')

        # Make sure no tftp test files are present on the target b
        lines = b.send_and_return_all('cd tftpdir')
        lines = b.send_and_return_all('rm ' + file_name)
        lines = b.send_and_return_all('cd ..')
        lines = b.send_and_return_all('ls tftpdir')
        if verify_existence(lines, file_name) == True:
            raise test_fail('File %s not deleted' % (file_name))

        # Create the file in TFTP server b
        lines = b.send_and_return_all('cd tftpdir')
        lines = b.send_and_return_all('tftp -c ' + file_name)
        lines = b.send_and_return_all('cd ..')
        lines = b.send_and_return_all('ls tftpdir')
        if verify_existence(lines, file_name) == False:
                raise test_fail('File %s not found' % (file_name))

        # Make sure no tftp test files are present on the target a
        lines = a.send_and_return_all('rm ' + file_name)
        lines = a.send_and_return_all('ls')
        if verify_existence(lines, file_name) == True:
            raise test_fail('File %s not deleted' % (file_name))

        # Gets files from 'tftp server' b
        lines = a.send('tftp ' + b.ip(v6).addr + ' get ' + file_name)
        a.expect_exact_and_wait_prompt('Transfer completed:')
        lines = a.send_and_return_all('ls')
        if verify_existence(lines, file_name) == False:
            raise test_fail('File %s not found' % (file_name))

        # Make sure no tftp test files are present on the target b
        lines = b.send_and_return_all('cd tftpdir')
        lines = b.send_and_return_all('rm ' + file_name)
        lines = b.send_and_return_all('cd ..')
        lines = b.send_and_return_all('ls tftpdir')
        if verify_existence(lines, file_name) == True:
            raise test_fail('File %s not deleted' % (file_name))

        # Copy files from 'a' to 'b'
        a.send('tftp ' + b.ip(v6).addr + ' put ' + file_name)
        a.expect_exact_and_wait_prompt('Transfer completed:')
        lines = b.send_and_return_all('ls tftpdir')
        if verify_existence(lines, file_name) == False:
            raise test_fail('File %s not found' % (file_name))

###########################################################################
## tftp_check_working_directory
###########################################################################
class tftp_check_working_directory:
    'checking working directory'

    def config(self):
        self.hosts = 2
        self.require_types = [ 'ipnet', 'ipnet' ]
        self.eta = 6

    def test(self, log, hosts, v6, _):
        'checking working directory'
        (a, b) = hosts
        file_name = '../check.txt'

        #enabled allow.upload
        a.set_sysvar('iptftps.allow.upload', 'enable')
        
        b.send('tftp ' + a.ip(v6).addr + ' get ' + file_name)
        b.expect_re_and_wait_prompt("ERROR: Code=2 Msg=\"Could not access file aboved working directory.\"")

###########################################################################
# End of file
###########################################################################

