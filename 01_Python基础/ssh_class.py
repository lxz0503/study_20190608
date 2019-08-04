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
            self.s = s     # 这个很关键，有了self.s，你就可以做很多其他事情，例如在其他方法里实现拷贝或者执行其他脚本
        except pxssh.ExceptionPxssh as e:
            print(e)

    def disconnect(self):
        self.s.logout()

    # 下面这个函数只能执行一些linux系统标准命令，或者执行一些可执行脚本，最好用全路径,不带参数
    def send_cmd(self, runcmd):
        self.s.sendline(runcmd)
        self.s.prompt()
        print(self.s.before)
        return self.s.before

    # 下面可以实现文件拷贝,从其他server拷贝到另外一台server，可以添加类似的例如修改文件名等方法
    def transfer_file(self, src, dst):
        self.s.sendline('scp %s %s' % (src, dst))
        self.s.prompt()
        print(self.s.before)
        return self.s.before

    # 下面可以实现修改文件名等方法,在本地移动文件到其他目录
    def mv_file(self, src, dst):
        self.s.sendline('mv %s %s' % (src, dst))
        self.s.prompt()
        print(self.s.before)
        return self.s.before

    # 执行一些非系统命令，例如运行脚本，后面带参数那种
    def set_env(self, dvd_path):
        self.s.sendline("cd %s" % dvd_path)
        self.s.prompt()
        self.s.sendline("./wrenv.sh -p helix")
        self.s.prompt()

    # 执行一些脚本,这是关键处理点
    def run_script(self, ip, port):
        # cmd = "20-参数解析parameter-getopt.py -h -i " + ip + " -p " + port + " 2>&1 | tee test.log"
        self.s.sendline('20-参数解析parameter-getopt.py -h -i %s -p %d 2>&1 | tee test.log' % (ip, port))
        self.s.prompt()
        res = self.s.before
        # 对res进行判断处理
        print(res)


# 函数调用
def real_ssh_test(ssh_config, cmd):
    ssh = SshTest(ssh_config['host_name'], ssh_config['username'], ssh_config['password'])
    ssh.connect()
    ssh.run_script("10.0.0.1", 80)          # 测试这里
    for i in cmd:
        ssh.send_cmd(i)
    ssh.disconnect()


if __name__ == "__main__":
    ssh_config = {'host_name':'128.224.163.8', 'username':'windriver', 'password':'windriver'}
    # cmd = ['uname -a', 'cat /proc/version']
    src_file = "/home/windriver/1.txt"
    dst_file = "/home/windriver/2.txt"
    cmd = "mv " + src_file + " " + dst_file     # 提前组合好要执行的命令
    real_ssh_test(ssh_config, cmd)

    # 最终目标是能执行下面的类似命令，即在远端运行某个脚本，而不单单运行系统命令
    # sshToAnvlServer = ssh(opt)
    # sshToAnvlServer.send_and_wait_prompt('cd /root/ANVL-automation')
    # '\n<<<<<<<<<<     start to execute ANVL suite "%s"     >>>>>>>>\n' % suite
    # sshToAnvlServer.s.sendline('./ANVL.py -t %s -c all -s %s -l %s -v %s 2>&1 | tee anvl.log'%(opt['bsp'], suite, AnvlLogFolder, opt['vxworks']))
    # j = sshToAnvlServer.s.expect([sshToAnvlServer.prompt, 'Press return and reboot DUT:'])

    # 可以用下面的方式执行系统命令，但是如果ssh或者telnet之后就不行了
    # 注意这种执行方式是没有参数的，必须提前拼接好命令，或者括号里就是能直接执行的命令
    # build_cmd = r'/home/windriver/ANVL/buildRTNet.sh'
    # os.system(build_cmd)
    # tmpDir = "/home/windriver/SPIN" + "/" + spin
    # os.chdir(tmpDir)
    # os.system("cp -rf * /home/windriver/SPIN/")
