#!/usr/bin/env python3

import pexpect
import os, time,logging,sys

class TelTarget(object):
    def __init__(self):
        # self.log = sys.stdout
        self.log = open("logfile.txt", 'wb')   # in py3 it is wb,in py2 it is w
        self.ip = "128.224.164.57"
        self.port = 16
        self.conn = None

    def connect_target(self):
        tcmd = "telnet %s %s" % (self.ip, self.port + 2000)
        self.conn = pexpect.spawn(tcmd)
        self.conn.logfile = self.log
        self.conn.sendline(os.linesep)   # in my env,you should send a \n or \r\n
        for _ in range(10):
            i = self.conn.expect(['VxWorks Boot]:',
                               '->',
                               'Press any key to stop auto-boot...',
                               pexpect.TIMEOUT,
                               pexpect.EOF], 1000)
            # print("i=%s\n" % i)
            if i == 0:
                break
            if i == 1:
                print(self.conn.before.decode('utf-8'))
                break
            if i == 2:
                break
            if i == 3 or i == 4:
                sys.exit(1)

    def disconnect(self):
        if self.conn is not None:
            self.conn.sendcontrol(']')
            self.conn.expect('telnet> ')
            self.conn.sendline('q')
            self.conn.expect('Connection closed.')
            self.conn = None
            self.log.close()

    def sendAndReturnAll(self, cmd, expect, timeout=20):
        '''return the lines not empty, each line gets stripped'''
        if self.conn is not None:
            # logging.debug('\n--- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
            self.conn.sendline(cmd)
            self.conn.expect(expect, timeout=timeout)
            return self.conn.before.decode('utf-8')
            # return lines    # change bytes to string
        else:
            print("error")

if __name__ == '__main__':
    tel = TelTarget()
    tel.connect_target()
    r = tel.sendAndReturnAll('version', '->')
    print(r)
    tel.disconnect()