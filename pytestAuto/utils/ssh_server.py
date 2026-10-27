#!/usr/bin/env python3
import os
import re
import sys
import tempfile
import time
import pexpect

sys.path.insert(0, '.')
from shellUtils import run_cmd

# xiaozhan---use below line to debug---python3 vlmTarget_dev.py
# from shellUtils import run_cmd

debugFlag = True

ubuntu_nwk2 = {
    'IP': '128.224.153.29',
    'username': 'xli3',
    'pwd': '3333xli3',
    'sshPrompt': 'Are you sure you want to continue connecting',
    'pwdPrompt': 'assword:',
    'osPrompt': 'xli3@pek-vx-nwk2'
}

vlmServerConfigs = {
    # Ubuntu20.04
    'pek-vx-nwk2': ubuntu_nwk2,
}

debugFlag = True  # boolean to turn on/off debug log


class VLMException(Exception):
    pass


class SshServer():

    def __init__(self, id):
        assert id in vlmServerConfigs.keys()
        self.checkPexpectVersion()
        self.id = id
        self.bootTimeout = 30
        self.conn = None
        self.debug = True

        self.IP = vlmServerConfigs[id]['IP']
        self.username = vlmServerConfigs[id]['username']
        self.pwd = vlmServerConfigs[id]['pwd']
        self.sshPrompt = vlmServerConfigs[id]['sshPrompt']
        self.pwdPrompt = vlmServerConfigs[id]['pwdPrompt']
        self.osPrompt = vlmServerConfigs[id]['osPrompt']

    def connect(self, timeout=30):
        cmdSSH = 'ssh %s@%s' % (self.username, self.IP)
        print("ssh cmdSSH=%s\n" % cmdSSH)
        s = pexpect.spawn(cmdSSH)
        for _ in range(2):
            i = s.expect([self.sshPrompt,
                          self.pwdPrompt,
                          pexpect.TIMEOUT,
                          pexpect.EOF])
            print("ssh i=%s\n" % i)
            if i == 0:
                s.sendline('yes')
            if i == 1:
                s.sendline(self.pwd)
                s.expect(self.osPrompt)
                break
            if i == 2 or i == 3:
                print("ERROR!: cannot ssh to server!\n")
                sys.exit(1)
        self.conn = s

    def disconnect(self):
        if self.conn is not None:
            self.conn.sendcontrol('c')
            self.conn.expect(self.osPrompt)
            self.conn.sendline('exit')
            self.conn.expect('logout')
            self.conn = None
        return

    def checkPexpectVersion(self):
        if pexpect.__version__ < '4.2.1':
            print('pexpect version %s not supported, should be 4.2.1 or later' % pexpect.__version__)
            sys.exit(1)

    def connClose(self):
        self.disconnect()

    def send(self, cmd):
        if self.conn:
            self.conn.sendline(cmd)
        else:
            raise VLMException('self.conn not set up')

    def expect(self, expect, timeout=20):
        if self.conn is not None:
            # print('\n--- expect="%s" within %s seconds' % (expect, timeout))
            return self.conn.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.conn not set up')

    def sendAndExpect(self, cmd, expect, timeout=30):
        if self.conn is not None:
            self.conn.sendline(cmd)
            self.conn.expect(expect, timeout=timeout)
            # print('---before=|%s|' % self.conn.before)
        else:
            raise VLMException('self.conn not set up')

    def sendAndReturnAll(self, cmd, expect, timeout=30): 
        '''return the lines not empty, each line gets stripped'''
        if self.conn is not None:
            self.conn.sendline(cmd)
            self.conn.expect(expect, timeout=timeout)
            rets = self.conn.before.decode('utf-8')
            rets = rets.lstrip('  ~]$').rstrip('[')   # xiaozhan, this depends on server configuration
            return rets  # xiaozhan this is string
        else:
            raise VLMException('self.conn not set up')

    def sendAndReturnAllByTimeout(self, cmd, cmd_timeout=30, strip_lines=True):
        '''
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result after cmd_timeout seconds.
        All lines are not stripped.
        This funtion is used for the command without any returned prompt/flag, like "route monitor"
        '''
        id, logfile = tempfile.mkstemp(prefix='tmp')  # /tmp
        # print('tempfile=%s' % logfile)
        magic_stop = 'stop_magic_stop'

        # save pexpect config
        old_timeout = self.conn.timeout
        old_logfile = self.conn.logfile

        with open(logfile, 'wb') as fdw:  # must be 'wb'
            self.conn.logfile = fdw

            self.conn.sendline(cmd)
            time.sleep(10)

            cmd1 = 'echo ' + magic_stop + '\n'
            self.conn.sendline(cmd1)
            self.conn.expect(magic_stop)

        # restore pexpect config
        self.conn.timeout = old_timeout
        self.conn.logfile = old_logfile

        with open(logfile, 'rb') as fdr:
            content = fdr.read().decode('utf-8')  # change to string
            # process content based on the original content, it may be different
            content = [line.strip().rstrip('\r\n') for line in content.split('\r\n') if line != '']

        run_cmd('rm -f %s' % logfile)
        # print('content is\n', content)
        return content


def ssh_nwk2():
    id = 'pek-vx-nwk2'
    nwk2 = SshServer(id)
    nwk2.connect()
    # below two lines are ok
    rets = nwk2.sendAndReturnAll('ifconfig', 'xli3@pek-vx-nwk2')
    print('rets\n', rets)
    #
    # try timeout
    rets = nwk2.sendAndReturnAllByTimeout('ping 127.0.0.1')
    res = rets[2:-1]
    print('rets\n', res)
    nwk2.connClose()
    # return nwk2


if __name__ == '__main__':
    ssh_nwk2()
