"""this is for ssh test """

# !/usr/bin/env python
# encoding = utf-8

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
            #f = open("logfile.txt",'w')  # record test log to a file
            #s.logfile = f   
            s.logfile = sys.stdout    
            self.s = s     # 
        except pxssh.ExceptionPxssh as e:
            print(e)

    def disconnect(self):
        self.s.logout()

    def send_cmd(self, runcmd):
        self.s.sendline(runcmd)
        self.s.prompt()
        print(self.s.before)
        return self.s.before
    
    def mv_file(self, src, dst):
        self.s.sendline('mv %s %s' % (src, dst))
        self.s.prompt()
        print(self.s.before)
        #return self.s.before

    def set_env(self, dvd_path):
        self.s.sendline("cd %s" % dvd_path)
        self.s.prompt()
        self.s.sendline("./wrenv.sh -p helix")
        self.s.prompt()

    def run_script(self, ip, port):
        self.s.sendline('python parameter-getopt.py -h -i %s -p %d 2>&1 | tee test.log' % (ip, port))
        self.s.prompt()
        res = self.s.before
        print(res)


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
    #ssh.mv_file(src_file, dst_file)
    ssh.disconnect()

