#!/folk/svc-cmnet/opt/bin/python

import argparse
import getpass
import os
import re
import sys
import pexpect
import socket
import subprocess
import pwd

from pexpect import pxssh
from multiprocessing import Pool

vmConfig = { 
            'tis-vm' : {
                        'kong-vm-tis-100-1' : '11247',
                        'kong-vm-tis-100-2' : '11248',
                        'kong-vm-tis-100-3' : '11249',
                        'kong-vm-tis-100-4' : '11250',
                        'kong-vm-tis-100-5' : '11244',
                        'kong-vm-tis-100-6' : '11215',
                        'kong-vm-tis-100-7' : '11216',
                        'kong-vm-tis-100-8' : '11253',
                        'kong-vm-tis-100-9' : '11218',
                        'kong-vm-tis-100-10' : '11219',
                        'kong-vm-tis-100-11' : '11245',
                        'kong-vm-tis-100-12' : '11246',
                     },
                 
            'revo-vm' : {
                        'kong-rvm-101' : '128.224.186.74',
                        'kong-rvm-102' : '128.224.186.24',
                        'kong-rvm-103' : '128.224.186.155',
                        'kong-rvm-104' : '128.224.186.118',
                        'kong-rvm-105' : '128.224.186.236',
                        'kong-rvm-106' : '128.224.186.156',
                        'kong-rvm-107' : '128.224.186.234',
                        'kong-rvm-108' : '128.224.186.32',
                        'kong-rvm-109' : '128.224.186.240',
                        'kong-rvm-110' : '128.224.186.214',
                        'kong-rvm-111' : '128.224.186.241',
                        'kong-rvm-112' : '128.224.186.249',
                      },
            
            'real-machine' : {
                        'pek-testharness-s1' : '128.224.159.128',
                      }
            }


def Log(outputStr):
    print '=== (%s) ' % os.getpid() + outputStr

def runShCmd(cmd):
    #print 'cmd %s', cmd
    p = subprocess.Popen(cmd,bufsize=1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out, std_err = p.communicate()
    #print 'std_out : %s' % std_out
    return (p.returncode, std_out)

class SSH(object):
    def __init__(self, hostName, user):
        self.hostName = hostName
        self.user = user
        self.sshHostFile = self.__GetSSHHostFile()
        self.s = None
            
    def __GetSSHHostFile(self):
        hostFileTmp = '/folk/{logname}/.ssh/known_hosts'
        return hostFileTmp.format(logname = getpass.getuser())

    def Disconnect(self):
        self.s.logout()
        
    def SendCmd(self, cmd):
        if self.s is not None:
            self.s.sendline(cmd)
            self.s.prompt()
            print (self.s.before)
            return self.s.before
        else:
            return None
                    
        
class SSHTiS(SSH):
    def __init__(self, hostName, user, keyFile):
        self.keyFile = keyFile
        self.natServer = '128.224.179.25'
        super(SSHTiS, self).__init__(hostName, user)

        
    def Connect(self):
        try:
            self.__DeleteOffendKey(self.sshHostFile, self.natServer)
            port = vmConfig['tis-vm'].get(self.hostName, None)
            if port is not None:
                s = pxssh.pxssh(timeout=60*60) # set up a larget timeout 
                s.login(server = self.natServer, username = self.user, port = port, ssh_key = self.keyFile)
                self.s = s
        except pxssh.ExceptionPxssh as e:
            print("pxssh failed on login.")
            print(e)

            
    def __DeleteOffendKey(self, sshHostFile, hostname):
        with open(sshHostFile, 'r') as fd:
            lines = fd.readlines()
        
        with open(sshHostFile, 'w') as fd:
            newLines = [ x for x in lines if not x.startswith(hostname) ]
            for x in newLines:
                fd.write(x)

      
class SSHRevo(SSH):
    def __init__(self, hostName, user, password):
        self.password = password
        super(SSHRevo, self).__init__(hostName, user)
        
    def Connect(self):
        try:
            ip = vmConfig['revo-vm'].get(self.hostName, None)
            if ip is not None:
                s = pxssh.pxssh(timeout=60*60) # set up a larget timeout since it takes time to copy a large file remote VM
                s.login(server = ip, username = self.user, password = self.password)
                self.s = s
        except pxssh.ExceptionPxssh as e:
            print("pxssh failed on login.")
            print(e)


class SSHRealMachine(SSH):
    def __init__(self, hostName, user, password):
        self.password = password
        super(SSHRealMachine, self).__init__(hostName, user)
        
    def Connect(self):
        try:
            ip = vmConfig['real-machine'].get(self.hostName, None)
            if ip is not None:
                s = pxssh.pxssh(timeout=60*60) # set up a larget timeout since it takes time to copy a large file remote VM
                s.login(server = ip, username = self.user, password = self.password)
                self.s = s
        except pxssh.ExceptionPxssh as e:
            print("pxssh failed on login.")
            print(e)
            
            
def runCmdAtTiSVM(hostName, cmd):
    keyFile = '/folk/lchen3/kong.key'
    print '=== handle ', hostName
    ssh = SSHTiS(hostName, 'ubuntu', keyFile)
    ssh.Connect()
    ssh.SendCmd(cmd)
    ssh.Disconnect()
    

def runCmdAtRevoVM(hostName, cmd):
    user = 'revo'
    password = 'revouser'
    print '=== handle ', hostName
    ssh = SSHRevo(hostName, user, password)
    ssh.Connect()
    ssh.SendCmd(cmd)
    ssh.Disconnect()


updateUml = 'sudo cp -f /net/pek-vx-nightly3/buildarea3/lchen3/uml/uml/ubuntu_root_fs /uml/ubuntu_root_fs; diff /net/pek-vx-nightly3/buildarea3/lchen3/uml/uml/ubuntu_root_fs /uml/ubuntu_root_fs; echo $?; sudo chmod 755 /uml/ubuntu_root_fs; ls -l /uml/ubuntu_root_fs'

updateUmlToSsh102 = 'cd /; sudo rm -fr /uml; sudo tar xvf /net/pek-vx-nightly3/buildarea3/lchen3/uml/uml-ssh-1.0.2.tar; sudo chmod 755 /uml/ubuntu_root_fs; ls -l /uml/bin/lib/libcrypto.so.1.0.0'

updateUmlToSsh098 = 'cd /; sudo rm -fr /uml; sudo tar xvf /net/pek-vx-nightly3/buildarea3/lchen3/uml/uml-ssh-0.9.8.tar; sudo chmod 755 /uml/ubuntu_root_fs; ls -l /uml/bin/lib/libcrypto.so.0.9.7'

# used to re-setup TiS VMs, e.g. after power recycle
setupHostNameTpl = 'cat /etc/hosts | grep -v "127.0.0.1" > newhosts; echo "127.0.0.1 {hostName}" >> newhosts; sudo cp newhosts /etc/hosts; cat /etc/hosts'

restoreGitAtTiS = 'cd /home/ubuntu; rm -fr vxworks; git clone http://$USER@stash.wrs.com/scm/vx7/vxworks vxworks; cd vxworks; ./setup-tools'
restoreGitAtRevo = 'cd /home/revo; rm -fr vxworks; git clone http://$USER@stash.wrs.com/scm/vx7/vxworks vxworks; cd vxworks; ./setup-tools'

listVxWorksRevo = 'cd /home/revo/jenkins; ls -l'
listVxWorksTis = 'cd /home/ubuntu/jenkins; ls -l'

showKongEnv = 'pgrep vxsim; pgrep uml_switch; ip link; brctl show'
clearKongEnv = 'pkill vxsim; pkill uml_switch; ip link; brctl show'

# rounds: 1.  tests_ok: 72.  tests_fail: 1.  tests_skipped: 0.

def findKongDev(content):
    return re.findall('(?s): (rs.*?):', content)
    
    
def cleanKongEnv(hostName):
    print '=== handle ', hostName

    if hostName.startswith('kong-vm-tis'):
        keyFile = '/folk/%s/kong.key' % pwd.getpwuid(os.getuid())[0] # cannot use os.getlogin()
        ssh = SSHTiS(hostName, 'ubuntu', keyFile)

    if hostName.startswith('kong-rvm-'):    
        user = 'revo'
        password = 'revouser'
        ssh = SSHRevo(hostName, user, password)

    if hostName.startswith('pek-testharness-s'):
        user = 'svc-cmnet'
        password = 'december2012!'
        ssh = SSHRealMachine(hostName, user, password)

    ssh.Connect()
        
    content = ssh.SendCmd('ip link')
    devs = findKongDev(content)
    for dev in devs:
        ssh.SendCmd('sudo ip link delete %s' % dev)
    if devs:
        ssh.SendCmd('ip link')
    
    cmds = ('sudo pkill vxsim',
            'sudo pkill uml_switch',
           )
    for cmd in cmds:
        ssh.SendCmd(cmd)
    
    ssh.SendCmd('brctl show')

    ssh.Disconnect()


def parseArgument():
    parser = argparse.ArgumentParser('Run Kong Test at VM')
    parser.add_argument('-', action='store', dest='gitDir', help='git directory')
    parser.add_argument('-d', action='store', dest='imageDir', help='image directory')
    parser.add_argument('-s', action='store', dest='commitSuccess', help='commmit for success')
    parser.add_argument('-f', action='store', dest='commitFailure', help='commmit for failure')
    parser.add_argument('-m', action='store', dest='module', help='module')
    parser.add_argument('-c', action='store', dest='test', help='test cases')
    r = parser.parse_args()
    
    if (r.commitSuccess is None) or (r.commitFailure is None) or \
       (r.module is None) or (r.test is None) or (r.imageDir is None):
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(r.gitDir):
        print 'git path %s not existed' % r.gitDir
        sys.exit(2)
        
    if not os.path.exists(r.imageDir):
        print 'image path %s not existed' % r.imageDir
        sys.exit(3)
        
    return r

class VxGit(object):
    def GetSearchingCommits(self, commitSuccess, commitFailure, parallelTestNum=1):
        pass
    
    def CheckoutCommit(self, commit):
        pass
    

class ImageBuilder(object):
    def __init__(self, gitDir, module, testCase):
        self.gitDir = gitDir
        self.module = module
        self.testCase = testCase
        
    def Build(self):
        cmd = './runKong.sh -g %s -m %s buildOnly 2>&1 | tee build.log'
        ret, result = runShCmd(cmd)
        
            
    
    def CheckBuild(self):
        pass
    
    def MoveImage(self):
        pass
    
    
def main():
    r = parseArgument()
    print r
    
    builder = ImageBuilder(r.gitDir, r.imageDir, r.module, r.test)
    builder.Build()
    sys.exit(0)

    """
    for host in sorted(vmConfig['tis-vm']) + sorted(vmConfig['revo-vm']) + sorted(vmConfig['real-machine']):
        if host not in ('fake-kong-rvm1'):
            #print host
            cleanKongEnv(host)
    """     

        
if __name__ == '__main__':
    main()
    
