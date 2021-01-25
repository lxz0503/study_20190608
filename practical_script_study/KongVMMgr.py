#!/folk/svc-cmnet/opt/bin/python

# must use this python since it has pexpect module

import getpass
import os
import re
import sys
import pexpect
import socket
import pwd

from pexpect import pxssh
from multiprocessing import Pool

vmConfig = { 
            'tis-vm' : {
                        'kong-vm-tis-100-1' : '11251',
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
                        'pek-testharness-s1' : '128.224.158.6',
                      }
            }


def Log(outputStr):
    print '=== (%s) ' % os.getpid() + outputStr

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
            print('ip=%s' % ip)
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
runHostCmdTpl = 'sudo hostnamectl set-hostname {hostName}'

pingHostNameTpl = 'ping -c 2 {hostName}'

restoreGitAtTiS = 'cd /home/ubuntu; rm -fr vxworks; git clone http://$USER@stash.wrs.com/scm/vx7/vxworks vxworks; cd vxworks; ./setup-tools'
restoreGitAtRevo = 'cd /home/revo; rm -fr vxworks; git clone http://$USER@stash.wrs.com/scm/vx7/vxworks vxworks; cd vxworks; ./setup-tools'

listVxWorksRevo = 'cd /home/revo/jenkins; ls -l'
listVxWorksTis = 'cd /home/ubuntu/jenkins; ls -l'

showKongEnv = 'pgrep vxsim; pgrep uml_switch; ip link; brctl show'
clearKongEnv = 'pkill vxsim; pkill uml_switch; ip link; brctl show'

installCsh = 'sudo apt-get install csh -y; which csh'
listTime = 'date'

syncTimeRevo = 'sudo ln -sf /usr/share/zoneinfo/Etc/UTC  /etc/localtime; sudo cat /etc/ntp.conf | grep -Ev "^pool|^server" > ntp.conf.new; echo "pool ntp-1.wrs.com" >> ntp.conf.new; echo "pool ntp-2.wrs.com" >> ntp.conf.new; sudo cp ntp.conf.new /etc/ntp.conf; rm -f ntp.conf.new; sudo /etc/init.d/ntp stop; sudo /usr/sbin/ntpdate ntp-1.wrs.com; sudo /etc/init.d/ntp start; date'
syncTimeTiS  = 'sudo ln -sf /usr/share/zoneinfo/Etc/UTC  /etc/localtime; sudo /usr/sbin/ntpdate ntp-1.wrs.com; date'

setUTCTimeZone = 'sudo ln -sf /usr/share/zoneinfo/Etc/UTC  /etc/localtime; date'

installYaml = 'sudo pip --trusted-host pypi.org --no-cache-dir --proxy 147.11.252.42:9090 install PyYAML'
installYamlAtLocal = 'sudo pip --proxy 147.11.252.42:9090 install PyYAML'

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

# commands

def cleanKongEnviron():
    for host in sorted(vmConfig['tis-vm']) + sorted(vmConfig['revo-vm']) + sorted(vmConfig['real-machine']):
        if host not in ('kong-rvm-107'):
            cleanKongEnv(host)

def setZone():
    for host in sorted(vmConfig['tis-vm']):
        if host not in ('kong-vm-tis-fake'):
            runCmdAtTiSVM(host, setUTCTimeZone)

    for host in sorted(vmConfig['revo-vm']):
        if host not in ('kong-rvm-fake',):
            runCmdAtRevoVM(host, setUTCTimeZone)

        
def main():
    """
    for host in sorted(vmConfig['tis-vm']):
        if host not in ('kong-vm-tis-fake'):
            pingHostNameCmd = pingHostNameTpl.format(hostName=host)
            runCmdAtTiSVM(host, pingHostNameCmd)
            #runCmdAtTiSVM(host, installYamlAtLocal)
    """
    for host in sorted(vmConfig['revo-vm']):
        if host not in ('kong-rvm-fake',):
            setupHostName = setupHostNameTpl.format(hostName=host)
            runCmdAtRevoVM(host, setupHostName)
            pingHostNameCmd = pingHostNameTpl.format(hostName=host)
            runCmdAtRevoVM(host, pingHostNameCmd)
            #runHostCmd = runHostCmdTpl.format(hostName=host)
            #runCmdAtRevoVM(host, installYaml)
    #"""

        
if __name__ == '__main__':
    main()
    #setZone()
