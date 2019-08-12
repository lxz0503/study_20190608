"""this is for ssh test with spawn """
# if you want to ssh to another server and run some interactive command like scp, ftp
# you must use spawn but not pxssh

# !/usr/bin/env python
# encoding = utf-8

import sys, re
from pexpect import pxssh
import pexpect
class SshTest(object):
    def __init__(self, host_name, user_name, password):
        self.host_name = host_name
        self.user_name = user_name
        self.password = password
        self.s = None

    def connect(self):
        try:
            cmdSSH = 'ssh windriver@128.224.163.8'
            s = pexpect.spawn(cmdSSH)
            s.logfile = sys.stdout
            #f = open("spawn.log",'w')
            #sys.stdout = f
            for i in range(2):
                i = s.expect(['windriver@PEK-QCAO1-D2:~',
                                 'assword:',
                                 'Are you sure you want to continue connecting',
                                 pexpect.TIMEOUT,
                                 pexpect.EOF]) 
                if i == 2:
                    s.sendline('yes')
                if i == 1:
                    s.sendline("windriver")
                    s.expect('windriver@PEK-QCAO1-D2:~')
                    break
                if i == 0:
                    break
                if i == 3 or i == 4:
                    print("ERROR!: cannot ssh to server!")
                    break
        except Exception:
            print("exception")
        self.s = s       # 这个赋值很关键，后续都会用到这个self.s

    def disconnect(self):
        self.s.close()

    def send_cmd(self, runcmd):
        self.s.sendline(runcmd)
        self.s.expect("windriver@PEK-QCAO1-D2:~")
        #print(self.s.before)

    # ssh到其他server上面再执行一些交互命令，很实用
    def transfer_file(self, src, dst):
        self.s.sendline('scp %s %s' % (src, dst))
        for i in range(2):
            i = self.s.expect(['assword:', 'Are you sure you want to continue connecting',pexpect.TIMEOUT]) 
            if i == 1:
                self.s.sendline('yes')
            if i == 0:
                self.s.sendline("3333xli3")
                self.s.expect("00:00")
                break
            if i == 2:
                print("copy log timeout!")
                break
    def mv_file(self, src, dst):
        self.s.sendline('mv %s %s' % (src, dst))
        self.s.expect("windriver@PEK-QCAO1-D2:~")

# ssh到其他server上面去执行脚本，很实用
    def run_script(self, ip, port):
        self.s.sendline('python parameter-getopt.py -h -i %s -p %d 2>&1 | tee test.log' % (ip, port))
        self.s.expect("windriver@PEK-QCAO1-D2:~")


if __name__ == "__main__":
    ssh_config = {'host_name':'128.224.163.8', 'username':'windriver', 'password':'windriver'}
    cmd = ['uname -a', 'cat /proc/version']
    src_file = "/home/windriver/1.txt"
    dst_file = "/home/windriver/2.txt"
    #cmd = "mv " + src_file + " " + dst_file     # 
    ssh = SshTest(ssh_config['host_name'], ssh_config['username'], ssh_config['password'])
    ssh.connect()
    for i in cmd:
        ssh.send_cmd(i)
    ssh.run_script("10.0.0.1", 80)
    ssh.mv_file(src_file, dst_file)
    src = "/home/windriver/2.txt"
    dst = "xli3@128.224.156.156:/workspace/share/kong-05/xli3/xiaozhan_python"
    ssh.transfer_file(src, dst)
    ssh.disconnect()

