"""this is for ssh test """

# !/usr/bin/env python

import sys, re
from pexpect import pxssh
class SshTest(object):
    def __init__(self, host_name, user_name, password):
        self.host_name = host_name
        self.user_name = user_name
        self.password = password
        self.s = None

    def connect(self):
        try:
            s = pxssh.pxssh(timeout=60*60)
            s.login(server=self.host_name, username=self.user_name, password=self.password)
            # f = open("logfile.txt",'w')  # record test log to a file
            # s.logfile = f   # log记录到文件里面,disconnect之后这个文件描述符自动关闭
            s.logfile = sys.stdout    # log输出到屏幕上
            self.s = s
        except pxssh.ExceptionPxssh as e:
            print(e)

    def disconnect(self):
        self.s.logout()

    def send_cmd(self, runcmd):
        self.s.sendline(runcmd)
        self.s.prompt()
        print(self.s.before)
        return self.s.before

# 函数调用
def real_ssh_test(ssh_config, cmd):
    ssh = SshTest(ssh_config['host_name'], ssh_config['username'], ssh_config['password'])
    ssh.connect()
    for i in cmd:
        ssh.send_cmd(i)
    ssh.disconnect()


if __name__ == "__main__":
    ssh_config = {'host_name':'128.224.163.8', 'username':'windriver', 'password':'windriver'}
    cmd = ['uname -a', 'cat /proc/version']
    real_ssh_test(ssh_config, cmd)
