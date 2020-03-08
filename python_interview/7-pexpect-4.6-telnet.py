#!/usr/bin/env python
# ???????
# [xli3@pek-sec-kong-02 xli3]$ python3 7-pexpect-4.6-telnet.py
# here
# hhhhh
# aaaaaa
# gei(2,0)host:/home/windriver/SPIN/vip_itl_generic/default/vxWorks e=128.224.166.238:0xfffffe00 h=128.224.163.8 g=128.224.166.1 u=windriver pw=windriver
import logging
import pexpect
import os,re
import time,sys

class Telnet(object):
    def __init__(self):
        self.t = None

    def connect(self, addr, port):
        bootLine = '@gei(2,0)host:/home/windriver/SPIN/vip_itl_generic/default/vxWorks e=128.224.166.238:0xfffffe00 h=128.224.163.8 g=128.224.166.1 u=windriver pw=windriver f=0x00'
        cmdTelnet = 'telnet %s %s' % (addr, port)
        self.t = pexpect.spawn(cmdTelnet)
        self.t.send(os.linesep)
        for _ in range(10):
            i = self.t.expect(['VxWorks Boot]:',
                               '->',
                               'Press any key to stop auto-boot...',
                               pexpect.TIMEOUT,
                               pexpect.EOF], 30)
            if i == 0:
                self.t.sendline(bootLine)
                time.sleep(10)
                self.t.expect('->')
                break

            if i == 1:
                # debug by xiaozhan
                print("here")
                self.t.sendline('reboot')
                self.t.expect('vxTarget')
                self.t.send(os.linesep)
                self.t.expect(':')
                print("hhhhh")
                self.t.sendline(bootLine)
                print("aaaaaa")
                self.t.expect('->', timeout=None)
                break
            # debug by xiaozhan
            if i == 2:
                self.t.send(os.linesep)
                continue

            if i == 3 or i == 4:
                sys.exit(1)

    def disconnect(self):
        if self.t is not None:
            self.t.sendcontrol(']')
            self.t.expect('telnet> ')
            self.t.sendline('q')
            self.t.expect('Connection closed.')
            self.t = None
        return

    def run_cmd(self):
        l = []
        self.t.sendline('version')
        self.t.expect('->')
        r = self.t.before.split(b'\r\n')
        for line in r:
            l.append(line.decode('utf-8').strip())
        return l
        #return filter(lambda x: x!='',
           #map(lambda x: x.decode('utf-8').strip(), r))


if __name__ == '__main__':
    conn = Telnet()
    conn.connect('128.224.164.57', 2016)
    res = conn.run_cmd()
    #print(res)   
    for i in res:
        #print(i)
        r = re.search(r'^gei.*',i)
        if r is not None:
            print(r.group())    # print(i)
            break
    conn.disconnect()


