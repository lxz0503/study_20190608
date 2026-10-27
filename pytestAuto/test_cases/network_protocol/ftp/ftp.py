
#############################################################################
#
# Copyright (c) 2017-2018, 2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#

'This test verifies the functionality of the IPFTP client and server'

import re
import util
import subprocess
import pexpect
import socket

ftp_debug = False

def clean_up_targets(targets):

    # Delete all target dirs with the prefix 'dir_'
    # Delete all target files with the prefix 'fil_'
    def remove_files_and_dirs(t):
        lines = t.send_and_return_all('ls')
        #print lines
        for line in lines:
            for item in line.split():
                #print 'Item: ' + str(item)
                if re.match('dir_', item) != None:
                    #print 'Dir: ' + str(item)
                    t.send_and_return_all('cd ' + item)
                    remove_files_and_dirs(t)
                    t.send_and_return_all('cd ..')
                    t.send_and_return_all(t.rmdir_cmd + item)
                if re.search('fil_', item) != None:
                    #print 'File: ' + str(item)
                    t.send_and_return_all('rm ' + item)

    for t in targets:
        #print 'target: ' + t.login_ip().addr
        remove_files_and_dirs(t)

class myspawn(pexpect.spawn):
    def __init__(self, cmd, lf, *args, **kwargs):
        pexpect.spawn.__init__(self, cmd, *args, **kwargs)
        try:
            self.setlog(lf)
        except:
            self.logfile = lf
        self.lf = lf

    def send(self, s):
        self.lf.write(s)
        return pexpect.spawn.send(self, s)

def telnet_login_ftp_ctrl(logfile, ip, port = 21, login = True, banner = False):
    #ftps_ctrl = pexpect.spawn('telnet ' + str(ip.addr) + ' ' + str(port))
    ftps_ctrl = myspawn('telnet ' + str(ip.addr) + ' ' + str(port), logfile.l.logfile)
    if banner:
        ftps_ctrl.expect ('Login Banner #1\r\n(.*?)ready\.\r\n')        
    else:
        ftps_ctrl.expect ('ready\.\r\n')
    fs_root = None
    if login:
        ftps_ctrl.send('USER ftp\r')
        ftps_ctrl.expect ('331 Password required for user ftp\r\n')
        ftps_ctrl.send('PASS interpeak\r')
        ftps_ctrl.expect ('230 Login OK\r\n')

        ftps_ctrl.send('PWD\r')
        ftps_ctrl.expect ('257 \"(.*)/?\" is current directory\r\n')
        fs_root = ftps_ctrl.match.group(1)
        if fs_root[-1] == '/':
            fs_root = fs_root[:-1]

    return ftps_ctrl, fs_root

    
def telnet_logout_ftp_ctrl(ftps_ctrl):

    ftps_ctrl.send('QUIT\r')
    ftps_ctrl.expect ('221 Bye\r\n')


def ftp_send_and_return_all(ftpc, cmd, prompt = 'ftp> ', append = ''):
    '''uses pexpect
    returns a list of all lines of output, stripped of crap like leading/trailing whitespace.'''
    ftpc.send(cmd.strip() + append)
    ftpc.expect(prompt)
    all = ftpc.s.s.before

    all = all.replace('\r\n\x00', '')

    lines0 = all.split('\r\n') #split lines. this is pty style newlines.
    lines0 = lines0[1:] # all but cmd
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


def ftp_expect_prompt_and_match_response(ftpc, response, prompt = '\r\n'):

    ftpc.expect(prompt)
    cmd = ftpc.before
    ftpc.expect(prompt)
    line = ftpc.before
    if re.match(response, line) == None:
        print '\nCommand: \'' + cmd + '\'\nExpected: \'' + response+ '\' Got: \'' + line + '\'\n'


def ftp_verify_response(lines, response, cmd_only = True, offset = 0):

    if cmd_only: # Filter out all non-cmd channel lines
        j = 0
        while len(lines[j:]):
            if re.match('[1-9][0-9][0-9] ', lines[j]) == None:
                lines = lines[0:j] + lines[j + 1:]
            else:
                j += 1

    response = response[offset:]

    if ftp_debug:
        print 'Got:      ' + str(lines)
        print 'Expected: ' + str(response)

    if len(response) > len(lines):
        raise test_fail('Too few lines in response')
    match = None
    for i in range(len(response)):
        match = re.match(response[i], lines[i])
        if match == None:
            raise test_fail('Response mismatch ('  + lines[i] + ' != ' + response[i])

    return lines, match

def ftp_verify_lineset(set1, set2, subset = True):
    aset = set(set1)
    bset = set(set2)
    if subset:
        if len(aset - bset) != 0:
            raise test_fail('Response mismatch'  + str(set1) + str(set2))
    else:
        if len(aset - bset) == 0:
            raise test_fail('Response mismatch'  + str(set1) + str(set2))

def ftp_wait_for_response(ftpc, response):
#    resp = ftpc.expect('[1-9][0-9][0-9] [^\r\n]*\r\n')
    resp = ftpc.expect('[1-9][0-9][0-9] ')
    if resp != response + '\r\n':
        print 'Got:      ', resp
        print 'Expected: ', response


def ftp_find_response_line(regex, lines):
    for line in lines:
        if re.search(regex, line) != None:
            return line
    return None


def ftp_login(ftpc, ftps, ftpuser = 'ftp', ftppasswd = 'interpeak', passive = 0, extended = 0):

    if ftp_debug:
        print ''
        print 'ftp_login ip:' + ftps.ip().addr + ' u: ' + str(ftpuser) + ' pwd: ' + str(ftppasswd) + ' passive: ' + str(passive) + ' extended: ' + str(extended)

    ftps.set_sysvar('ipftps.tls.cert_file', 'ftp_tls.cert')
    ftps.set_sysvar('ipftps.tls.enable', '1')
    ftps.set_sysvar('ipftps.tls.key_file', 'ftp_tls.cert')
    ftps.set_sysvar('ipftps.tls.private.enable', '0')

    # ftp_send_and_return_all(ftpc, 'ftp -t -k ftp_tls.cert -c ftp_tls.cert -s P -C')
    ftp_send_and_return_all(ftpc, 'ftp')
    ftp_send_and_return_all(ftpc, 'passive ' + str(passive))
    ftp_send_and_return_all(ftpc, 'extended ' + str(extended))
    ftp_send_and_return_all(ftpc, 'open ' + ftps.ip().addr, prompt = 'User: ')
    ftp_send_and_return_all(ftpc, ftpuser, prompt = 'Password: ')
    ftp_send_and_return_all(ftpc, ftppasswd)

    lines = ftp_send_and_return_all(ftpc, 'pwd')
    _, m = ftp_verify_response(lines, ['257 \"(.*)/?\" is current directory'])
    x = m.groups()[0]
    if x[-1] == '/':
        return x[:-1]
    return x


def ftp_logout(ftpc):
    ftpc.send_and_return_all('quit')


# Private IP Range: 10.0.0.0 to 10.255.255.255
def get_invalid_private_ipaddr(ipaddr):
    assert type(ipaddr) == str
    octets = [int(x) for x in ipaddr.split('.')]
    newOctet1 = octets[1] + 1
    if newOctet1 > 255:
        newOctet1 = 0
    return '.'.join([str(x) for x in [octets[0], newOctet1, octets[2], octets[3]]])


###########################################################################
# Test classes
###########################################################################

class cmd_before:
    'Server command before logged in'

    def config(self):
        self.hosts = 1
        self.eta = 16
        self.v6 = True

    def test(self, log, target, v6, _):

        ftpuser = 'ftp'
        ftppasswd = 'interpeak'

        ftps, fs_root = telnet_login_ftp_ctrl(log, target.login_ip(), login = False)

        def send_expect(t, cmd, rply):

            t.send(cmd)
            t.expect(cmd + '\n')
            t.expect('[^\r\n]+\r\n')
            if t.after != rply:
                print 'Got: \'' + t.after + '\' Expected: \'' + rply + '\''

        ftps.send('ABOR\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('ACCT\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('APPE\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('CDUP\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('CWD\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('DELE\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('LIST\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('MKD\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('MODE\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('NLST\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('NOOP\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('PASV\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('PORT\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('PWD\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('RETR\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('RMD\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('RNFR\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('RNTO\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('STAT\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('STOR\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('STRU\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('SYST\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('TYPE\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('XCUP\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('XCWD\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('XMKD\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('XPWD\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('XRMD\r')
        ftps.expect('530 Login required\r\n')
        ftps.send('HELP\r')
        ftps.expect('211 Use HELP <cmd> for help on cmd\r\n')

        send_expect(ftps, 'PASS\r', '501 Invalid number of arguments\r\n')

        for i in range(2):
            ftps.send('USER ' + ftpuser + '\r')
            ftps.expect('331 Password required for user ' + ftpuser + '\r\n')
            ftps.send('PASS nogood\r')
            ftps.expect('530 Authorization failed\r\n')

        ftps.send('USER ' + ftpuser + '\r')
        ftps.expect('331 Password required for user ' + ftpuser + '\r\n')
        ftps.send('PASS nogood\r')
        ftps.expect('421 Service not available, closing control connection\r\n')

        ftps, fs_root = telnet_login_ftp_ctrl(log, target.login_ip(), login = False)

        ftps.send('USER ' + ftpuser + '\r')
        ftps.expect('331 Password required for user ' + ftpuser + '\r\n')
        ftps.send('PASS ' + ftppasswd + '\r')
        ftps.expect ('230 Login OK\r\n')

        ftps.send('USER ' + ftpuser + '\r')
        ftps.expect ('503 Cannot change user\r\n')

        ftps.send('PASS ' + ftppasswd + '\r')
        ftps.expect ('503 Already logged in\r\n')

        telnet_logout_ftp_ctrl(ftps)

#==========================================================================
# login_banner
#==========================================================================
class login_banner:
    'Verify login banner'

    def config(self):
        self.hosts = 1
        self.eta = 1
        self.v6 = True

    def test(self, log, target, v6, _):

        ftps, _ = telnet_login_ftp_ctrl(log, target.login_ip(), login = True, banner = True)

        telnet_logout_ftp_ctrl(ftps)      

#==========================================================================
# task_flag_checking
#==========================================================================
class task_flag_checking:
    'Verify if the flag of ftp server task is set VX_FP_TASK'

    def config(self):
        self.hosts = 1
        self.eta = 1
        self.v6 = False

    def test(self, log, target, v6, _):

        ftps = target

        ftps.send("ti ipftps")
        ftps.expect_re_and_wait_prompt("VX_FP_TASK")
        

#==========================================================================
# cmd_argno
#==========================================================================
class cmd_argno:
    'Verify commands with correct and incorrect number of arguments'

    def config(self):
        self.hosts = 1
        self.eta = 1
        self.v6 = True

    def test(self, log, target, v6, _):

        ftps, _ = telnet_login_ftp_ctrl(log, target.login_ip())

        ftps.send('ABOR x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('ACCT\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('ACCT x x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('APPE\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('APPE x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('CDUP x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('CWD\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('CWD x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('DELE\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('DELE x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('HELP x x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('LIST x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('MKD\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('MKD x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('MODE\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('MODE x x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('NLST x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('NOOP x x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('PASS\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('PASS x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('PORT 1,2,3,4,5\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('PORT 1,2,3,4,5,6,7\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('PWD x x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('RETR\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('RETR x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('RMD\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('RMD x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('RNFR\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('RNFR x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('RNTO\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('RNTO x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('STAT x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('STOR\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('STOR x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('STRU\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('STRU x x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('SYST x x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('TYPE\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('TYPE x x x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        #ftps.send('USER\r')
        #ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('USER x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('XCUP x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('XCWD\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('XCWD x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('XMKD\r')
        ftps.expect('501 Invalid number of arguments\r\n')
#        ftps.send('XMKD x x\r')
#        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('XPWD x\r')
        ftps.expect('501 Invalid number of arguments\r\n')
        ftps.send('XRMD\r')
        ftps.expect('501 Invalid number of arguments\r\n')

        telnet_logout_ftp_ctrl(ftps)

#==========================================================================
# cmd_misc
#==========================================================================
class cmd_misc:
    'Verify miscellaneous server commands'

    def config(self):
        self.hosts = 1
        self.eta = 1
        self.v6 = True

    def test(self, log, ftpserv, v6, _):
        ftps, _ = telnet_login_ftp_ctrl(log, ftpserv.login_ip())

        ftps.send('abor\r')
        ftps.expect ('226 No data connection\r\n')
        ftps.send('AbOr\r')
        ftps.expect ('226 No data connection\r\n')
        ftps.send('ABOR\r')
        ftps.expect ('226 No data connection\r\n')

        ftps.send('PASV\r')
        ftps.expect ('227 Entering passive mode \([0-9,]*\)\r\n')
        ftps.send('ABOR\r')
        ftps.expect ('226 Closing data connection\r\n')

        ftps.send('ACCT x\r')
        ftps.expect ('202 Command not implemented\r\n')

        ftps.send('HELP\r')
        ftps.expect ('211 Use HELP <cmd> for help on cmd\r\n')
        ftps.send('HELP help\r')
        ftps.expect ('214 HELP - Help\r\n')

        ftps.send('MODE S\r')
        ftps.expect ('200 Stream mode selected\r\n')
        ftps.send('MODE s\r')
        ftps.expect ('200 Stream mode selected\r\n')
        ftps.send('MODE B\r')
        ftps.expect ('504 Only S supported\r\n')

        ftps.send('NOOP\r')
        ftps.expect ('200 OK\r\n')

        ftps.send('STRU F\r')
        ftps.expect ('200 File structure selected\r\n')
        ftps.send('STRU f\r')
        ftps.expect ('200 File structure selected\r\n')
        ftps.send('STRU B\r')
        ftps.expect ('504 Only F supported\r\n')

        ftps.send('SYST\r')
        ftp_expect_prompt_and_match_response(ftps, '215 UNIX Type: L8')
#        ftps.expect ('215 UNIX Type: L8\r\n')

        ftps.send('TYPE A\r')
        ftps.expect ('200 Type A selected\r\n')
        ftps.send('TYPE A N\r')
        ftps.expect ('200 Type A N selected\r\n')
        ftps.send('TYPE A T\r')
        ftps.expect ('200 Type A T selected\r\n')
        ftps.send('TYPE I\r')
        ftps.expect ('200 Type I selected\r\n')
        ftps.send('TYPE L 8\r')
        ftps.expect ('200 Type L 8 selected\r\n')

        ftps.send('TYPE B\r')
        ftps.expect ('504 Only TYPE A ?N|T?, I and L 8 supported\r\n')
        ftps.send('TYPE A B\r')
        ftps.expect ('504 Only TYPE A ?N|T?, I and L 8 supported\r\n')
        ftps.send('TYPE L 9\r')
        ftps.expect ('504 Only TYPE A ?N|T?, I and L 8 supported\r\n')

        telnet_logout_ftp_ctrl(ftps)

#==========================================================================
# cmd_dir
#==========================================================================
class cmd_dir:
    'Verify directory related server commands'

    def config(self):
        self.hosts = 1
        self.eta = 1
        self.v6 = True

    def test(self, log, ftpserv, v6, _):

        clean_up_targets([ftpserv])

        ftps, fs_root = telnet_login_ftp_ctrl(log, ftpserv.login_ip())

        def send_expect(t, cmd, rply):

            t.send(cmd)
            t.expect(cmd + '\n')
            t.expect('[^\r\n]+\r\n')
            if not re.match(rply, t.after):
                print 'Got: \'' + t.after + '\' Expected: \'' + rply + '\''

        # Create relative directories
        ftps.send('PWD\r')
        ftps.expect ('257 \"' + fs_root + '/?\" is current directory\r\n')
        ftps.send('MKD dir_ftptest\r')
        ftps.expect ('257 \"dir_ftptest\" directory created\r\n')
        ftps.send('MKD dir_ftptest/dir_subdir\r')
        ftps.expect ('257 \"dir_ftptest/dir_subdir\" directory created\r\n')
        ftps.send('CWD dir_ftptest\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"' + fs_root + '/dir_ftptest/?\" is current directory\r\n')
        ftps.send('CDUP\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"' + fs_root + '/?\" is current directory\r\n')

        # Test obscure directories
        ftps.send('CWD ' + fs_root + '/dir_ftptest/dir_subdir/../dir_subdir\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect('257 \"' + fs_root + '/dir_ftptest/dir_subdir/?\" is current directory\r\n')
        ftps.send('CWD ' + fs_root + '/../dir_ftptest\r')
        ftps.expect ('550 .*\r\n')
        ftps.send('CWD ' + fs_root + '/dir_ftptest/../../dir_ftptest/dir_subdir\r')
        ftps.expect ('550 .*\r\n')

        # Remove directories
        ftps.send('CWD ' + fs_root + '/dir_ftptest\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('RMD .\r')
        # We're satisfied with any 550 message
        # since it differs with the ports
        ftps.expect ('550 .*\r\n')
        ftps.send('CWD ' + fs_root + '/\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"' + fs_root + '/?\" is current directory\r\n')
        ftps.send('RMD dir_ftptest/dir_subdir\r')
        ftps.expect ('250 Directory removed\r\n')
        ftps.send('RMD dir_ftptest\r')
        ftps.expect ('250 Directory removed\r\n')
        #ftps.send('CWD dir_ftptest\r')
        #ftps.expect ('550 .*\r\n')
        #ftps.send('CDUP\r')
        #ftps.expect ('550 No such file or directory\r\n')

        # Create absolute directories

        send_expect(ftps,'PWD\r', '257 \"' + fs_root + '/?\" is current directory\r\n')

        ftps.send('MKD dir_ftptest\r')
        ftps.expect ('257 \"dir_ftptest\" directory created\r\n')

        send_expect(ftps, 'MKD ' + fs_root + '/dir_ftptest/dir_subdir\r', '257 \"' + fs_root + '/dir_ftptest/dir_subdir\" directory created\r\n' )

        ftps.send('CWD dir_ftptest\r')
        ftps.expect ('250 CWD changed\r\n')

        # New root
        ftps.send('XFTP root ' + fs_root + '/dir_ftptest\r')
        ftps.expect ('200 OK\r\n')

        # Exercise the new root
        ftps.send('PWD\r')
        ftps.expect ('257 \"/?\" is current directory\r\n')

        ftps.send('CWD dir_subdir/\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"/dir_subdir/?\" is current directory\r\n')
        ftps.send('CWD ../dir_subdir\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"/dir_subdir/?\" is current directory\r\n')
        ftps.send('CWD /dir_subdir\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"/dir_subdir/?\" is current directory\r\n')

        ftps.send('CWD /dir_subdir/..\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"/?\" is current directory\r\n')
        ftps.send('CWD /dir_subdir/../dir_subdir\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"/dir_subdir/?\" is current directory\r\n')
        ftps.send('CWD /../dir_ftptest/dir_subdir\r')
        ftps.expect ('550 Permission denied\r\n')
        ftps.send('CWD /dir_subdir/../../dir_ftptest/dir_subdir\r')
        ftps.expect ('550 Permission denied\r\n')
        ftps.send('CWD /../dir_ftptest\r')
        ftps.expect ('550 Permission denied\r\n')
        ftps.send('CWD /dir_subdir/../../dir_ftptest\r')
        ftps.expect ('550 Permission denied\r\n')

        ftps.send('CDUP\r')
        ftps.expect ('250 CWD changed\r\n')
        ftps.send('CDUP\r')
        ftps.expect ('550 Permission denied\r\n')
        ftps.send('PWD\r')
        ftps.expect ('257 \"/?\" is current directory\r\n')

        send_expect(ftps, 'CWD /dir_subdir\r', '250 CWD changed\r\n')
        send_expect(ftps, 'PWD\r', '257 \"/dir_subdir/?\" is current directory\r\n')
        send_expect(ftps, 'CWD /\r', '250 CWD changed\r\n')
        send_expect(ftps, 'CDUP\r', '550 Permission denied\r\n')
        send_expect(ftps, 'PWD\r', '257 \"/?\" is current directory\r\n')

        # Remove absolute dirs
        send_expect(ftps, 'RMD /dir_subdir\r', '250 Directory removed\r\n')
        send_expect(ftps, 'CWD /dir_subdir\r','550 .*\r\n' )

        # Restore root
        send_expect(ftps,'XFTP root /\r', '200 OK\r\n')
        send_expect(ftps,'CWD ' + fs_root + '/\r', '250 CWD changed\r\n')
        send_expect(ftps, 'PWD\r', '257 \"' + fs_root + '/?\" is current directory\r\n')
        send_expect(ftps,'RMD ' + fs_root + '/dir_ftptest\r', '250 Directory removed\r\n')
        send_expect(ftps,'CWD ' + fs_root + '/dir_ftptest\r','550 .*\r\n')

        telnet_logout_ftp_ctrl(ftps)

#==========================================================================
# cmd_stat
#==========================================================================
class cmd_stat:
    'Verify the "stat" (session status) command'

    def config(self):
        self.hosts = 2
        self.eta = 2

    def test(self, log, targets, v6, _):
        (ftpc, ftps) = targets

        ftp_login(ftpc, ftps)

        lines = ftp_send_and_return_all(ftpc, 'quote stat')

        if v6:
            ipaddr_re = util.ip6_re
        else:
            ipaddr_re = util.ip_re

        ftp_verify_response(lines, ('211- Session status:',
                                    'Server: ' + str(ftps.ip().addr) + ' port 21',
                                    'Client: ' + ipaddr_re + ' port [1-9][0-9]{,4}'), cmd_only = False)

        ftp_logout(ftpc)

#==========================================================================
# cmd_transfer
#==========================================================================
class cmd_transfer:
    'Verify file transfer in various mode combinations (active, passive, extended, etc.)'

    def config(self):
        self.hosts = 2
        self.eta = 7

    def test(self, log, targets, v6, _):

        clean_up_targets(targets)

        def cmd_transfer(targets, passive, extended, v6 = False):

            if v6 and extended == 0:
                return

            (ftpc, ftps) = targets

            'Verify file transfer in various mode combinations (active, passive, extended, etc.)'
            fs_root = ftp_login(ftpc, ftps, passive = passive, extended = extended)

            lines = ftp_send_and_return_all(ftpc, 'pwd')
            ftp_verify_response(lines, ['257 \"' + fs_root + '/?\" is current directory'])
            lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest')
            ftp_verify_response(lines, ['257 \"dir_ftptest\" directory created'])
            lines = ftp_send_and_return_all(ftpc, 'cd dir_ftptest')
            ftp_verify_response(lines, ['250 CWD changed'])
            lines = ftp_send_and_return_all(ftpc, 'pwd')
            ftp_verify_response(lines, ['257 \"' + fs_root + '/dir_ftptest/?\" is current directory'])

            size = 10000

            if not v6:
                portmin = 192
            else:
                portmin = 49152

            if extended < 1:
                if passive == 0:
                    portok_or_enter = '200 Port OK'
                    dataconn = '150 Opening data connection'
                else:
                    portok_or_enter =  '227 Entering passive mode \([0-9]+,[0-9]+,[0-9]+,[0-9]+,([0-9]+),([0-9]+)\)'
                    dataconn = '125 Using existing data connection'
            else:
                if passive == 0:
                    portok_or_enter = '200 Extended port OK'
                    dataconn = '150 Opening data connection'
                else:
                    portok_or_enter = '229 Entering extended passive mode \(\|\|\|([0-9]+)\|\)'
                    dataconn = '125 Using existing data connection'

            mode = ('binary', 'ascii')
            mode_i = ('I', 'A')

            for i in range(2): # binary and ascii

                lines = ftp_send_and_return_all(ftpc, mode[i])
                ftp_verify_response(lines, ['200 Type ' + mode_i[i] + ' selected'])
                lines = ftp_send_and_return_all(ftpc, 'quote XFTP creat fil_1 ' + str(size))
                ftp_verify_response(lines, ['200 OK'])

                lines = ftp_send_and_return_all(ftpc, 'get fil_1')
                ftp_verify_response(lines, [portok_or_enter, dataconn, '226 Transfer complete'])
                if passive == 1:

                    if ftp_debug:
                        print re.match(portok_or_enter, lines[0]).groups()

                    port = int(re.match(portok_or_enter, lines[0]).groups()[0])
                    if extended == 0:
                        port = 256 * port + int(re.match(portok_or_enter, lines[0]).groups()[1])
                    if port < portmin:
                        raise test_fail('Too low port number\'' + str(port) + '\' < \'' + str(portmin) + '\'' )

                lines = ftp_send_and_return_all(ftpc, 'rename fil_1 fil_2')
                ftp_verify_response(lines, ['250 File renamed'])

                lines = ftp_send_and_return_all(ftpc, 'put fil_1')
                ftp_verify_response(lines, [portok_or_enter, dataconn, '226 Transfer complete'])
                if passive == 1:
                    port = int(re.match(portok_or_enter, lines[0]).groups()[0])
                    if extended == 0:
                        port = 256 * port + int(re.match(portok_or_enter, lines[0]).groups()[1])
                    if port < portmin:
                        raise test_fail('Too low port number\'' + str(port) + '\' < \'' + str(portmin) + '\'' )

                for filename in ('fil_1', 'fil_2'):
                    lines = ftp_send_and_return_all(ftpc, 'dir ' + filename)
                    ftp_verify_response(lines, [portok_or_enter, dataconn,'226 Transfer complete'])

                    line = ftp_find_response_line(filename, lines)
                    if re.match('-rw[-x]r[-w][-x]r[-w][-x]\s+[01]\s+\d+\s+\d+\s+10000.* ', line) == None:
                        raise test_fail('Invalid dir response')
                    if re.search(filename, line) == None:
                        raise test_fail('Invalid dir response')

                for filename in ('fil_1', 'fil_2'):
                    lines = ftp_send_and_return_all(ftpc, 'delete ' + filename)
                    ftp_verify_response(lines, ['250 File deleted'])

            lines = ftp_send_and_return_all(ftpc, 'cd ' + fs_root + '/')
            ftp_verify_response(lines, ['250 CWD changed'])
            lines = ftp_send_and_return_all(ftpc, 'rmdir ' + fs_root + '/dir_ftptest')
            ftp_verify_response(lines, ['250 Directory removed'])

            ftp_logout(ftpc)

        for p in (0, 1):
            for e in (0, 2):
                cmd_transfer(targets, p, e, v6)


#==========================================================================
# cmd_abort
#==========================================================================
class cmd_abort:
    'Verify that FTP transmission can be aborted'

    def config(self):
        self.hosts = 2
        self.eta = 2
        self.v6 = True

    def test(self, log, targets, v6, _):
        (ftpc, ftps) = targets
        clean_up_targets(targets)

        # Establish control channel
        ftps_ctrl, fs_root = telnet_login_ftp_ctrl(log, ftps.login_ip())

        # Create relative directories
        ftps_ctrl.send('MKD dir_ftptest\r')
        ftps_ctrl.expect ('257 \"dir_ftptest\" directory created\r\n')
        ftps_ctrl.send('CWD dir_ftptest\r')
        ftps_ctrl.expect ('250 CWD changed\r\n')
        ftps_ctrl.send('PWD\r')
        ftps_ctrl.expect ('257 \"' + fs_root + '/dir_ftptest/?\" is current directory\r\n')

        size = 820000

        ftps_ctrl.send('XFTP creat fil_1 ' + str(size) + '\r')
        #ftps_ctrl.expect("\n")
        #ftps_ctrl.expect("\n")
        #print ftps_ctrl.before
        #raise 'bork'
        ftps_ctrl.expect('200 OK\r\n')
        ftps_ctrl.send('PASV\r')

        ftps_ctrl.expect('\r\n')
        ftps_ctrl.expect('\r\n')
        line = ftps_ctrl.before

        # Establish data channel
        portobj = re.match('227 Entering passive mode \([0-9]+,[0-9]+,[0-9]+,[0-9]+,([0-9]+),([0-9]+)\)', line)
        portno = 256 * int(portobj.groups()[0]) + int(portobj.groups()[1])

        if ftp_debug:
            print 'Addr: ' + str(ftps.login_ip().addr) + ' port: ' + str(portno)

        csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        csock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000)
        csock.connect((ftps.login_ip().addr, portno))

        ftps_ctrl.send('RETR fil_1\r')
        ftps_ctrl.expect('125 Using existing data connection\r\n')

        csock.recv(4000)

        ftps_ctrl.send('STAT\r')
        ftps_ctrl.expect('\r\n')

        ftps_ctrl.send('ABOR\r')
        ftps_ctrl.expect('\r\n')
        for i in range(20):
            try:
                csock.recv(4000)
            except:
                pass
        ftps_ctrl.expect('426 Transfer aborted\r\n')
        ftps_ctrl.expect('226 Abort OK\r\n')

        # Close data channel
        csock.close()

        ftps_ctrl.send('DELE fil_1\r')
        ftps_ctrl.expect('\r\n')
        ftps_ctrl.expect('250 File deleted\r\n')
        ftps_ctrl.send('CDUP\r')
        ftps_ctrl.expect('\r\n')
        ftps_ctrl.expect('250 CWD changed\r\n')
        ftps_ctrl.send('RMD dir_ftptest\r')
        ftps_ctrl.expect('\r\n')
        ftps_ctrl.expect ('250 Directory removed\r\n')

        # Close control channel
        telnet_logout_ftp_ctrl(ftps_ctrl)

#==========================================================================
# cmd_proxy
#==========================================================================
class cmd_proxy:
    'Verify the FTP proxy feature'

    def cmd_proxy_in_lines(self, lines, txt, cnt = 1):
        for l in lines:
            if l == txt:
                cnt -= 1
        return (cnt == 0)

    def config(self):
        self.hosts = 2
        self.eta = 4
        self.v6 = False

    def test(self, log, targets, v6, _):
        (ftpc, ftps) = targets

        clean_up_targets(targets)

        'Verify the FTP proxy feature'
        fs_root = ftp_login(ftpc, ftps)

        lines = ftp_send_and_return_all(ftpc, 'pwd')
        ftp_verify_response(lines, ['257 \"' + fs_root + '/?\" is current directory'])
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest')
        ftp_verify_response(lines, ['257 \"dir_ftptest\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'cd dir_ftptest')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'pwd')
        ftp_verify_response(lines, ['257 \"' + fs_root + '/dir_ftptest/?\" is current directory'])

        size = 100

        lines = ftp_send_and_return_all(ftpc, 'quote XFTP creat fil_1 ' + str(size))
        ftp_verify_response(lines, ['200 OK'])

        lines = ftp_send_and_return_all(ftpc, 'binary')
        ftp_verify_response(lines, ['200 Type I selected'])

        lines = ftp_send_and_return_all(ftpc, 'get fil_1')
        ftp_verify_response(lines[2:], ['226 Transfer complete'])
        lines = ftp_send_and_return_all(ftpc, 'rename fil_1 fil_2')
        ftp_verify_response(lines, ['250 File renamed'])

        lines = ftp_send_and_return_all(ftpc, 'quote XFTP readonly 1')
        ftp_verify_response(lines, ['200 OK'])
        lines = ftp_send_and_return_all(ftpc, 'put fil_1')
        ftp_verify_response(lines[1:], ['550 Permission denied']) # RIME

        lines = ftp_send_and_return_all(ftpc, 'quote XFTP readonly 0')
        ftp_verify_response(lines, ['200 OK'])
        lines = ftp_send_and_return_all(ftpc, 'delete fil_2')
        ftp_verify_response(lines, ['250 File deleted'])

#        lines = ftp_send_and_return_all(ftpc, 'cd ' + fs_root + '/') # RIME
        lines = ftp_send_and_return_all(ftpc, 'cd ..')
        ftp_verify_response(lines, ['250 CWD changed'])
#        lines = ftp_send_and_return_all(ftpc, 'rmdir ' + fs_root + '/dir_ftptest')
        lines = ftp_send_and_return_all(ftpc, 'rmdir dir_ftptest')
        ftp_verify_response(lines, ['250 Directory removed'])

        # Try invalid address and port
        invalid_ipaddr = get_invalid_private_ipaddr(ftpc.ip().addr).replace('.', ',')
        lines = ftp_send_and_return_all(ftpc, 'quote PORT %s,4,0' % invalid_ipaddr)
        ftp_verify_response(lines, ['504 Invalid host'])

        # Try correct address but invalid port
        ipaddr = str(ftpc.ip().addr).replace('.', ',')
        lines = ftp_send_and_return_all(ftpc, 'quote PORT ' + ipaddr + ',3,255')
        ftp_verify_response(lines, ['504 Invalid port'])

        # Try with disabled proxy
        lines = ftp_send_and_return_all(ftpc, 'quote PASV')
        addr_port = re.match('227 Entering passive mode \(([0-9]+,[0-9]+,[0-9]+,[0-9]+),([0-9]+),([0-9]+)\)', lines[0]).groups()
        ipaddr = addr_port[0].replace(',', '.')
        port = str(256 * int(addr_port[1]) + int(addr_port[2]))

        lines = ftp_send_and_return_all(ftpc, 'quote XFTP connect 127.0.0.1 ' + ipaddr + ' ' +  port)
        ftp_verify_response(lines, ['200 OK'])
        lines = ftp_send_and_return_all(ftpc, 'quote NLST')
        ftp_verify_response(lines, ['425 Invalid host'])

        # Verify with enabled proxy
        lines = ftp_send_and_return_all(ftpc, 'quote XFTP proxy 1')
        ftp_verify_response(lines, ['200 OK'])

        lines = ftp_send_and_return_all(ftpc, 'quote PASV')
        addr_port = re.match('227 Entering passive mode \(([0-9]+,[0-9]+,[0-9]+,[0-9]+),([0-9]+),([0-9]+)\)', lines[0]).groups()
        ipaddr = addr_port[0].replace(',', '.')
        port = str(256 * int(addr_port[1]) + int(addr_port[2]))

        lines = ftp_send_and_return_all(ftpc, 'quote XFTP connect 127.0.0.1 ' + ipaddr + ' ' +  port)
        ftp_verify_response(lines, ['200 OK'])

        lines = ftp_send_and_return_all(ftpc, 'quote NLST')

        cnt = 0
        while '226 Transfer complete' not in lines:
            lines += ftp_send_and_return_all(ftpc, 'quote XFTP proxy 0')
            cnt += 1

        if '125 Using existing data connection' not in lines:
            raise test_fail('Missing response 125 ...')

        while not self.cmd_proxy_in_lines(lines, '200 OK', cnt):
            lines += ftp_send_and_return_all(ftpc, 'quote XFTP proxy 0')
            cnt += 1

        # Try with low port base = 0
        lines = ftp_send_and_return_all(ftpc, 'quote XFTP proxy 0')
        ftp_verify_response(lines, ['200 OK'])
        lines = ftp_send_and_return_all(ftpc, 'quote XFTP lportbase 0')
        ftp_verify_response(lines, ['200 OK'])

        lines = ftp_send_and_return_all(ftpc, 'quote PASV')
        addr_port = re.match('227 Entering passive mode \(([0-9]+,[0-9]+,[0-9]+,[0-9]+),([0-9]+),([0-9]+)\)', lines[0]).groups()
        ipaddr = addr_port[0].replace(',', '.')
        portno = 256 * int(addr_port[1]) + int(addr_port[2])

        lines = ftp_send_and_return_all(ftpc, 'quote XFTP connect 127.0.0.1 ' + ipaddr + ' ' + str(portno))
        ftp_verify_response(lines, ['200 OK'])
        lines = ftp_send_and_return_all(ftpc, 'quote NLST')
        ftp_verify_response(lines, ['425 Invalid host'])

        lines = ftp_send_and_return_all(ftpc, 'quote XFTP lportbase 49151')
        ftp_verify_response(lines, ['200 OK'])

        ftp_logout(ftpc)

#==========================================================================
# cmd_nlst_wildcard
#==========================================================================
class cmd_nlst_wildcard:
    'Verify file path with wild cards'

    def config(self):
        self.hosts = 2
        self.eta = 7

    def test(self, log, targets, v6, _):

        clean_up_targets(targets)

        (ftpc, ftps) = targets

        fs_root = ftp_login(ftpc, ftps, passive = 0, extended = 0)

        # Create relative directories
        lines = ftp_send_and_return_all(ftpc, 'pwd')
        ftp_verify_response(lines, ['257 \"' + fs_root + '/?\" is current directory'])
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest')
        ftp_verify_response(lines, ['257 \"dir_ftptest\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest1')
        ftp_verify_response(lines, ['257 \"dir_ftptest1\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_testftp')
        ftp_verify_response(lines, ['257 \"dir_testftp\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest/dir_subdir')
        ftp_verify_response(lines, ['257 \"dir_ftptest/dir_subdir\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest/dir_subdir1')
        ftp_verify_response(lines, ['257 \"dir_ftptest/dir_subdir1\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest/dir_dirsub')
        ftp_verify_response(lines, ['257 \"dir_ftptest/dir_dirsub\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'cd ' + fs_root + '/dir_ftptest/dir_subdir')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'pwd')
        ftp_verify_response(lines, ['257 \"' + fs_root + '/dir_ftptest/dir_subdir/?\" is current directory'])

        # Create files
        size = 1000
        mode = ('binary')
        mode_i = ('I')
        lines = ftp_send_and_return_all(ftpc, mode)
        ftp_verify_response(lines, ['200 Type ' + mode_i + ' selected'])
        lines = ftp_send_and_return_all(ftpc, 'quote XFTP creat fil_1 ' + str(size))
        ftp_verify_response(lines, ['200 OK'])
        lines = ftp_send_and_return_all(ftpc, 'quote XFTP creat fil_2 ' + str(size))
        ftp_verify_response(lines, ['200 OK'])
        lines = ftp_send_and_return_all(ftpc, 'quote XFTP creat 1_fil_ ' + str(size))
        ftp_verify_response(lines, ['200 OK'])

        # Validate
        lines = ftp_send_and_return_all(ftpc, 'cd ' + fs_root + '/')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'pwd')
        ftp_verify_response(lines, ['257 \"' + fs_root + '/?\" is current directory'])
        lines = ftp_send_and_return_all(ftpc, 'ls')
        ftp_verify_lineset(['dir_testftp', 'dir_ftptest', 'dir_ftptest1'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls *')
        ftp_verify_lineset(['dir_testftp', 'dir_ftptest', 'dir_ftptest1'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls ' + fs_root + '/*')
        ftp_verify_lineset([fs_root + '/dir_testftp', fs_root + '/dir_ftptest', fs_root +'/dir_ftptest1'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls ./*')
        ftp_verify_lineset(['./dir_testftp', './dir_ftptest', './dir_ftptest1'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls *ftptest?')
        ftp_verify_lineset(['dir_ftptest', 'dir_ftptest'], lines, False)
        lines = ftp_send_and_return_all(ftpc, 'ls *testft?')
        ftp_verify_lineset(['dir_ftptest', 'dir_ftptest1'], lines, False)
        lines = ftp_send_and_return_all(ftpc, 'ls ' + fs_root + '/dir_ftptest/*')
        ftp_verify_lineset([fs_root + '/dir_ftptest/dir_subdir', fs_root + '/dir_ftptest/dir_subdir1', fs_root + '/dir_ftptest/dir_dirsub'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls ' + fs_root + '/dir_ftptest/*subdir?')
        ftp_verify_lineset([fs_root + '/dir_ftptest/dir_subdir', fs_root + '/dir_ftptest/dir_dirsub'], lines, False)
        lines = ftp_send_and_return_all(ftpc, 'ls ' + fs_root + '/dir_ftptest/*dirsu?')
        ftp_verify_lineset([fs_root + '/dir_ftptest/dir_subdir', fs_root + '/dir_ftptest/dir_subdir1'], lines, False)
        lines = ftp_send_and_return_all(ftpc, 'ls ' + fs_root + '/dir_ftptest/dir_subdir/*')
        ftp_verify_lineset([fs_root + '/dir_ftptest/dir_subdir/fil_1', fs_root + '/dir_ftptest/dir_subdir/fil_2', fs_root + '/dir_ftptest/dir_subdir/1_fil_'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls ' + fs_root + '/dir_ftptest/dir_subdir/fil*')
        ftp_verify_lineset([fs_root + '/dir_ftptest/dir_subdir/1_fil_'], lines, False)
        lines = ftp_send_and_return_all(ftpc, 'ls ' + fs_root + '/dir_ftptest/dir_subdir/1_?i*')
        ftp_verify_lineset([fs_root + '/dir_ftptest/dir_subdir/fil_1', fs_root + '/dir_ftptest/dir_subdir/fil_2'], lines, False)

        lines = ftp_send_and_return_all(ftpc, 'cd dir_ftptest')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'pwd')
        ftp_verify_response(lines, ['257 \"' + fs_root + '/dir_ftptest/?\" is current directory'])
        lines = ftp_send_and_return_all(ftpc, 'ls *')
        ftp_verify_lineset(['dir_subdir', 'dir_subdir1', 'dir_dirsub'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls ./*')
        ftp_verify_lineset(['./dir_subdir', './dir_subdir1', './dir_dirsub'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls dir_sub*')
        ftp_verify_lineset(['dir_dirsub'], lines, False)
        lines = ftp_send_and_return_all(ftpc, 'ls ????dir*')
        ftp_verify_lineset(['dir_subdir', 'dir_subdir1'], lines, False)

        lines = ftp_send_and_return_all(ftpc, 'cd dir_subdir')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'pwd')
        ftp_verify_response(lines, ['257 \"' + fs_root + '/dir_ftptest/dir_subdir/?\" is current directory'])
        lines = ftp_send_and_return_all(ftpc, 'ls *')
        ftp_verify_lineset(['fil_1', 'fil_2', '1_fil_'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls ./*')
        ftp_verify_lineset(['./fil_1', './fil_2', './1_fil_'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls *fi*')
        ftp_verify_lineset(['fil_1', 'fil_2', '1_fil_'], lines)
        lines = ftp_send_and_return_all(ftpc, 'ls 1_*')
        ftp_verify_lineset(['fil_1', 'fil_2'], lines, False)
        lines = ftp_send_and_return_all(ftpc, 'ls *1')
        ftp_verify_lineset(['fil_2', '1_fil_'], lines, False)
        lines = ftp_send_and_return_all(ftpc, 'ls ??fi*')
        ftp_verify_lineset(['1_fil_'], lines)

        # Clean up directories and files
        lines = ftp_send_and_return_all(ftpc, 'cd ' + fs_root + '/dir_ftptest/dir_subdir/')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'delete fil_1')
        ftp_verify_response(lines, ['250 File deleted'])
        lines = ftp_send_and_return_all(ftpc, 'delete fil_2')
        ftp_verify_response(lines, ['250 File deleted'])
        lines = ftp_send_and_return_all(ftpc, 'delete 1_fil_')
        ftp_verify_response(lines, ['250 File deleted'])
        lines = ftp_send_and_return_all(ftpc, 'cdup')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'rmdir dir_subdir')
        ftp_verify_response(lines, ['250 Directory removed'])
        lines = ftp_send_and_return_all(ftpc, 'rmdir dir_subdir1')
        ftp_verify_response(lines, ['250 Directory removed'])
        lines = ftp_send_and_return_all(ftpc, 'rmdir dir_dirsub')
        ftp_verify_response(lines, ['250 Directory removed'])
        lines = ftp_send_and_return_all(ftpc, 'cdup')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'rmdir dir_ftptest')
        ftp_verify_response(lines, ['250 Directory removed'])
        lines = ftp_send_and_return_all(ftpc, 'rmdir dir_ftptest1')
        ftp_verify_response(lines, ['250 Directory removed'])
        lines = ftp_send_and_return_all(ftpc, 'rmdir dir_testftp')
        ftp_verify_response(lines, ['250 Directory removed'])

        ftp_logout(ftpc)

#==========================================================================
# cmd_option
#==========================================================================
class cmd_option:
    'cmd option'

    def config(self):
        self.hosts = 2
        self.eta = 7

    def test(self, log, targets, v6, _):

        clean_up_targets(targets)

        (ftpc, ftps) = targets

        ftpc.send('ftp -h')
        # ftpc.expect_re_and_wait_prompt(" -s <C|P> Set data session protect mode")
        ftpc.expect_re_and_wait_prompt(" -e Disable command-line editing")
        ftpc.send('ftp -m')
        ftpc.expect_re_and_wait_prompt("ftp: option requires an argument -- m")
        ftpc.send('ftp -m 530')
        ftpc.expect_re_and_wait_prompt("FTP server: Not logged in")
        ftpc.send('ftp -m 226')
        ftpc.expect_re_and_wait_prompt("FTP server: Success, closing data connection")
        ftpc.send('ftp -m 1907')
        ftpc.expect_re_and_wait_prompt("FTP client: No more sessions allowed")
        ftpc.send('ftp -m 1901')
        ftpc.expect_re_and_wait_prompt("FTP client: Session is busy")
        ftpc.send('ftp -m 299')
        ftpc.expect_re_and_wait_prompt("General: Success")
        if v6:
            portok_or_enter = '200 Extended port OK'
            ftp_send_and_return_all(ftpc, 'ftp -P 21 -a 6 -p 0 -x 0 -l 6000 -r 30000 -v 2 -i -e')
        else:
            portok_or_enter = '200 Port OK'
            ftp_send_and_return_all(ftpc, 'ftp -P 21 -a 4 -p 0 -x 0 -l 6000 -r 30000 -v 2 -i -e')
        ftp_send_and_return_all(ftpc, 'open ' + ftps.ip().addr, prompt = 'User: ')
        ftp_send_and_return_all(ftpc, 'ftp', prompt = 'Password: ')
        ftp_send_and_return_all(ftpc, 'interpeak')

        lines = ftp_send_and_return_all(ftpc, 'pwd')
        _, m = ftp_verify_response(lines, ['257 \"(.*)/?\" is current directory'])
        x = m.groups()[0]
        if x[-1] == '/':
            fs_root =  x[:-1]
        else:
            fs_root = x

        # Create relative directories
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest')
        ftp_verify_response(lines, ['257 \"dir_ftptest\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'mkdir dir_ftptest/dir_subdir')
        ftp_verify_response(lines, ['257 \"dir_ftptest/dir_subdir\" directory created'])
        lines = ftp_send_and_return_all(ftpc, 'cd ' + fs_root + '/dir_ftptest/dir_subdir')
        ftp_verify_response(lines, ['250 CWD changed'])
        lines = ftp_send_and_return_all(ftpc, 'pwd')
        ftp_verify_response(lines, ['257 \"' + fs_root + '/dir_ftptest/dir_subdir/?\" is current directory'])

        # Create files
        size = 1000
        mode = ('binary')
        mode_i = ('I')
        lines = ftp_send_and_return_all(ftpc, mode)
        ftp_verify_response(lines, ['200 Type ' + mode_i + ' selected'])
        lines = ftp_send_and_return_all(ftpc, 'quote XFTP creat fil_1 ' + str(size))
        ftp_verify_response(lines, ['200 OK'])

        # do cmd
        lines = ftp_send_and_return_all(ftpc, 'get fil_1')
        ftp_verify_response(lines, [portok_or_enter, '150 Opening data connection', '226 Transfer complete'])
        lines = ftp_send_and_return_all(ftpc, 'append fil_1 fil_1')
        ftp_verify_response(lines, [portok_or_enter, '150 Opening data connection', '226 Transfer complete'])
        lines = ftp_send_and_return_all(ftpc, 'rhelp')
        ftp_verify_response(lines, ['211 Use HELP <cmd> for help on cmd'])
        lines = ftp_send_and_return_all(ftpc, 'rstatus')
        ftp_verify_response(lines, ['211 End of status'])
        lines = ftp_send_and_return_all(ftpc, 'system')
        ftp_verify_response(lines, ['215 UNIX Type: L8 Version: IPFTPS 6.8'])

        #local cmd
        lines = ftp_send_and_return_all(ftpc, 'lpwd')
        pos = lines[0].find('Current client directory is "')
        if pos == -1:
            raise test_fail('Can not parse local path')
        fc_root = lines[0][pos+29:-1]
        ftpc.send('lcd ' + fc_root)
        ftpc.expect('Current client directory is \"' + fc_root + '\"')
        ftpc.send('verbose')
        ftpc.expect('Verbose level: 2')
        ftpc.send('help')
        ftpc.expect (' verbose')
        ftpc.send('status')
        ftpc.expect ('Command-line editing: off')
        lines = ftp_send_and_return_all(ftpc, 'quote ALLO parameter ')
        ftpc.expect ('202 Command not implemented')

        ftp_logout(ftpc)



 #==========================================================================
# mutil_client
#==========================================================================
class mutil_ftp_client:
    'mutil_ftp_client'

    def config(self):
        self.eta = 15
        self.hosts = 3
        #self.v6 = False
        self.user = 'ftp'
        self.pwd = 'interpeak'
        self.ftpprompt = "ftp>"
        self.prompt = "->"
        self.port = 2323
        self.exitprompt = "Au revoir!"
        self.require_types = ['ipnet', 'ipnet', 'ipnet', 'ipnet']

    def test(self, log, targets, v6, _):

        c,s,p = targets

        c.send("ftp %s" % s.ip().addr)
        c.expect_exact('User:')

        c.send(self.user)
        c.expect_exact('Password:')

        c.send(self.pwd)
        c.expect_exact('230 Login OK')
        c.expect_re('200' + '.*?')
        c.expect_exact(self.ftpprompt)

        c.send('pwd')
        c.expect_re('257' + '.*?')
        c.expect_exact(self.ftpprompt)

        p.send('C')
        p.expect_exact('-> ')
        p.send('telnet \"%s\",%d' % (c.ip().addr,self.port))
        p.expect_exact('login: ')
        p.send(self.user)
        p.expect_exact('Password:')
        p.send(self.pwd)
        p.expect_exact(self.prompt)   

        #open second ftp client in c
        p.send("cmd ftp %s" % p.ip().addr)
        p.expect_exact('User:')

        p.send(self.user)
        p.expect_exact('Password:')

        p.send(self.pwd)
        p.expect_exact('230 Login OK')
        p.expect_re('200' + '.*?')
        p.expect_exact(self.ftpprompt)

        # check if the input command can lock each other
        p.send('pwd')
        p.expect_re('257' + '.*?')       
        p.send('pwd')
        p.expect_re('257' + '.*?')

        c.send('pwd')
        c.expect_re('257' + '.*?')
        c.send('pwd')
        c.expect_re('257' + '.*?')

        p.send('pwd')
        p.expect_re('257' + '.*?')
        c.send('pwd')
        c.expect_re('257' + '.*?')


        #exit
        p.send('quit')
        p.expect_re('221 Bye')     

        p.send('exit')
        p.expect_re(self.exitprompt)
        p.expect_re(self.prompt)
        p.send('cmd')

        c.send('quit')
        c.expect_re_and_wait_prompt('221 Bye')  

        
