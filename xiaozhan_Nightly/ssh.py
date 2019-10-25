import os
import sys
import pexpect
import time
from pexpect import TIMEOUT

class Ssh(object):
    '''operates on a baselinux
    Expects passwordless sudo unless logged in as root.'''

    def __init__(self, opt):
        self.type = 'ssh'
        self.opt = opt
        self.prompt = self.opt['dvdPrompt']
        self.env = False
        # if self.opt.has_key('debug'):
        self.debug = self.opt['debug']
        self.vsbDir = ''
        self.sharedWorkspace = ''
        self.dstImageFolder = ''
        self.dstImageFolderIsCreate = False
        self.confRun = self.opt['run']
        self.dvdpath = os.path.abspath(self.opt['dvdPath'])
        self.vxworks = self.opt['vxworks']
        self.bsp = self.opt['bsp']
        self.tool = self.opt['tool']
        self.getCfgDir = False
        self.ipnetCfgPath = ''
        self.ipmcpCfgPath = ''
        self.ipcomCfgPath = ''
        self.iptcpSrcPath = ''
        self.iptcpCfgPath = ''
        s = _dummy()
        cmdSSH = 'ssh %s@%s' % (self.opt['dvdUser'], self.opt['dvdAddr'])
        if self.debug:
            print
            "ssh cmdSSH=%s\n" % cmdSSH
        s = pexpect.spawn(cmdSSH)
        for _ in range(2):
            i = s.expect([self.opt['dvdPrompt'],
                          'assword:',
                          'Are you sure you want to continue connecting',
                          pexpect.TIMEOUT,
                          pexpect.EOF])
            if self.debug:
                print
                "ssh i=%s\n" % i
                print
                "s.before=%s\n" % s.before
                print
                "s.after=%s\n" % s.after
            if i == 2:
                s.sendline('yes')
            if i == 1:
                s.sendline(self.opt['dvdPwd'])
                s.expect(self.opt['dvdPrompt'])
                if self.debug:
                    print
                    "s.sendline(self.opt['dvdPwd'])-> s.before=%s\n" % s.before
                    print
                    "s.sendline(self.opt['dvdPwd'])-> s.after=%s\n" % s.after
                break
            if i == 0:
                break
            if i == 3 or i == 4:
                print
                "ERROR!: cannot ssh to server %s!\n" % self.opt['dvdAddr']
                sys.exit(1)
        # cguo: no need to set prompt due to it is destroyed after vxWorks wrenv.linux
        # cmdSetPrompt = 'export PS1="'+self.prompt+'"'
        # s.sendline(cmdSetPrompt)
        self.s = s
        self.wait_prompt(cleanup=True)

    def backup_src_file(self, filefullpath, sudo=False):
        if self.debug:
            print
            "goto backup_src_file\n"
        if sudo:
            backup_cmd = "sudo cp " + filefullpath + " " + filefullpath + ".bak"
        else:
            backup_cmd = "cp " + filefullpath + " " + filefullpath + ".bak"
        self.wait_prompt(cleanup=True)
        self.s.sendline('ls ' + filefullpath + '.bak')
        i = self.s.expect(['No such file', self.prompt])
        if self.debug:
            print
            "goto backup_src_file i=%s\n" % i
            self.printExpectInfo('ls ' + filefullpath + '.bak')
        if i == 1:
            self.s.sendline("cp -f " + filefullpath + ".bak" + " " + filefullpath)
            j = self.s.expect(['\?', self.prompt])
            if self.debug:
                print
                "goto backup_src_file j=%s\n" % j
                self.printExpectInfo("cp -f" + filefullpath + ".bak" + " " + filefullpath)
            if j == 0:
                self.send_and_wait_prompt('y')
            return

        self.s.expect(self.prompt)
        self.wait_prompt(cleanup=True)
        self.s.sendline(backup_cmd)
        i = self.s.expect(['\?', self.prompt])
        if self.debug:
            self.printExpectInfo(backup_cmd)
        if i == 0:
            self.send_and_wait_prompt('n')  # If origin .bak is existing, the origin one should be useful
            self.send_and_wait_prompt("cp -f " + filefullpath + ".bak" + " " + filefullpath)
            self.send_and_wait_prompt('y')
        self.wait_prompt(cleanup=True)

    def recover_src_file(self, bakFile, sudo=False):
        if self.debug:
            print
            "goto recover_src_file\n"
        oriFile = bakFile.split('.bak')[0]
        self.wait_prompt(cleanup=True)
        self.s.sendline('ls ' + bakFile)
        i = self.s.expect(['No such file', self.prompt])
        if self.debug:
            self.printExpectInfo('ls ' + bakFile)
        if i == 0:
            print
            'ERROR!: the bak file "%s" used to recover is nonexistent!\n' % bakFile
        self.wait_prompt(cleanup=True)
        if sudo:
            cmdRecover = 'sudo mv ' + bakFile + ' ' + oriFile
        else:
            cmdRecover = 'mv ' + bakFile + ' ' + oriFile
        self.s.sendline(cmdRecover)
        i = self.s.expect(['\?', self.prompt])
        if self.debug:
            self.printExpectInfo(cmdRecover)
        if i == 0:
            self.send_and_wait_prompt('y')
        self.wait_prompt(cleanup=True)

    def modify_src_file(self, fileDir, fileName, CurCode, NewCode, sudo=False):
        if self.debug:
            print
            "goto modify_src_file\n"
        fileFullPath = fileDir + fileName
        cloneFilePath = fileDir + "clone.txt"

        if sudo:
            cmdClone = "sudo mv " + fileFullPath + " " + cloneFilePath
        else:
            cmdClone = "mv " + fileFullPath + " " + cloneFilePath
        self.s.sendline(cmdClone)
        i = self.s.expect(['\?', self.prompt])
        if self.debug:
            self.printExpectInfo(cmdClone)
        if i == 0:
            self.send_and_wait_prompt('y')

        self.wait_prompt(cleanup=True)
        if sudo:
            cmdSed = "sudo sed 's/" + CurCode + "/" + NewCode + "/g' " + cloneFilePath + " > " + fileFullPath
        else:
            cmdSed = "sed 's/" + CurCode + "/" + NewCode + "/g' " + cloneFilePath + " > " + fileFullPath
        self.send_and_wait_prompt(cmdSed)

        if sudo:
            cmdRmClone = "sudo rm -f " + cloneFilePath
        else:
            cmdRmClone = "rm -f " + cloneFilePath
        self.send_and_wait_prompt(cmdRmClone)

    def setEnv(self):
        if self.debug:
            print
            "goto setEnv\n"
            print
            "the dvdpath is %s" % self.dvdpath
        if self.env:
            return
        self.send_and_wait_prompt('cd ' + self.dvdpath)
        if self.vxworks.startswith('7') or self.vxworks.startswith('platform'):

            # if 6,7 or platform,run below command
            self.send_and_wait_prompt('./wrenv.linux -p vxworks-' + self.vxworks)
        elif self.vxworks.startswith('helix'):
            # if it is for vx7-integration,then it should be helix,run below command
            self.send_and_wait_prompt('./wrenv.linux -p helix')
        else:
            print
            "wrong vxworks!"
        if self.debug:
            self.send_and_wait_prompt('env')
        self.env = True

    def logout(self):
        if self.env:
            self.s.sendline('exit')
            self.s.expect(self.prompt)
            self.env = False
        self.s.sendline('exit')
        self.s.expect([pexpect.EOF, pexpect.TIMEOUT])

    def printExpectInfo(self, cmd):
        print
        "[%s] --> self.s.before='%s'\n" % (cmd, self.s.before)
        print
        "[%s] --> self.s.after='%s'\n" % (cmd, self.s.after)

    def send_and_wait_prompt(self, cmd, timeout=-1):
        self.s.sendline(cmd)
        self.wait_prompt(timeout)
        if self.debug:
            self.printExpectInfo(cmd)
        self.wait_prompt(cleanup=True)

    def wait_prompt(self, timeout=-1, cleanup=False):
        '''
        All input is read and discarded up till the NEXT prompt.
        If there is still text in the output stream after this, you have probably forgotten
        to "sync" with the prompt after previous commands and will have a terrible time finding
        out whats gone wrong.
        "cleanup" is only used if you need to perform cleanup of something not cleaned up by
        the test engine.
        (This is how the original tcl expect_prompt works.)
        '''
        try:
            self.s.expect(self.prompt, timeout)
        except pexpect.TIMEOUT:
            if not cleanup:
                print
                "wait_prompt clean -> get pexpect.TIMEOUT\n"
                raise

        except pexpect.EOF:
            if not cleanup:
                print
                "wait_prompt clean -> get pexpect.EOF\n"
                raise

    def transfer_file(self, src, dst, passwd):
        if self.debug:
            print
            "goto transfer_file"
        self.s.sendline('scp %s %s ' % (src, dst))
        for _ in range(2):
            i = self.s.expect(['assword:', 'Are you sure you want to continue connecting', pexpect.TIMEOUT])
            if self.debug:
                self.printExpectInfo('scp %s %s ' % (src, dst))
                print
                "transfer_file: i=%d\n" % i
            if i == 1:
                self.s.sendline('yes')
            if i == 0:
                self.s.sendline(passwd)
                self.s.expect(self.prompt)
                break
            if i == 2:
                print
                "copy log timeout!"
                break

    def transfer_folder(self, src, dst, passwd):
        self.s.sendline('scp -q -r %s %s ' % (src, dst))
        for _ in range(2):
            i = self.s.expect(['assword:', 'Are you sure you want to continue connecting'])
            if i == 1:
                self.s.sendline('yes')
            if i == 0:
                self.s.sendline(passwd)
                self.s.expect(self.prompt)
                break

    def vip_build(self):
        self.s.setmaxread(1001)
        self.send_and_wait_prompt('vxprj build')
        self.s.setmaxread(1)
        self.wait_prompt(cleanup=True)
        self.s.sendline('ls default/vxWorks')
        i = self.s.expect(['No such file', self.prompt])
        if self.debug:
            print
            'ls default/vxWorks -> self.s.before=%s\n' % self.s.before
            print
            'ls default/vxWorks -> self.s.after=%s\n' % self.s.after
        if i == 0:
            print
            'ERROR!: VIP build failed!\n'
            sys.exit(1)
        if i == 1:
            print
            'VIP build succussfully!\n'

    def setSharedWorkspace(self, sudo=False):
        if self.debug:
            print
            "goto setSharedWorkspace\n"
        if not self.sharedWorkspace:
            FolderPath = self.dvdpath + "/%sBuild-" % (self.confRun) + curTime
            if sudo:
                cmdCreateWorkspace = 'sudo mkdir ' + FolderPath
                cmdChmod = 'sudo chmod 777 -R ./'
            else:
                cmdCreateWorkspace = 'mkdir ' + FolderPath
                cmdChmod = 'chmod 777 -R ./'
                cmdCreateWorkspace = 'mkdir ' + FolderPath
                cmdChmod = 'chmod 777 -R ./'
                cmdCreateWorkspace = 'mkdir ' + FolderPath
                cmdChmod = 'chmod 777 -R ./'
            self.send_and_wait_prompt(cmdCreateWorkspace)
            self.send_and_wait_prompt('cd ' + FolderPath)
            self.send_and_wait_prompt(cmdChmod)
            self.sharedWorkspace = FolderPath
            if self.confRun == 'ANVL':
                self.dstImageFolder = self.opt['ftpdir'] + '/%s_%s_' % (self.confRun, self.vxworks) + curTime
            else:
                print
                'ERROR! You input invalid type "%s" with "-r(--run)". The valid is ANVL / TAHI\n' % self.confRun
                sys.exit(1)
        else:
            return

    def vsb_create_and_build(self, suite):
        if self.debug:
            print
            "goto vsb create\n"
        if self.confRun == 'ANVL':
            # self.transfer_file(self.opt['sshuser']+'@'+self.opt['localAddr']+':'+self.opt['pwd']+'/'+self.confRun+'_vsbcfg/'+'Vx'+(self.vxworks).split('.')[0]+'/vsb.config', self.sharedWorkspace, self.opt['sshpwd'])
            self.vsbDir = self.sharedWorkspace + '/VSB_%s' % (self.confRun)
            # =====add this parameter -inet for vx6,the default configuration for vx6 is IPv4. For vx7 the default configuraiton is IPv4 and IPv6.  xiaozhan =====#
            self.send_and_wait_prompt(
                'vxprj vsb create -S -lp64 -cpu CORE -smp -inet6 -profile DEVELOPMENT -bsp %s  %s' % (
                self.bsp, self.vsbDir), timeout=60)

        else:
            print
            'ERROR! You input invalid type "%s" with "-r(--run)". The valid is ANVL / TAHI \n' % self.confRun
            sys.exit(1)
        if self.debug:
            print
            "goto vsb build\n"
        # debug by xiaozhan,add \n
        self.send_and_wait_prompt('cd ' + self.vsbDir + '\n')
        if self.vxworks.startswith('6'):
            # self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y')
            # self.send_and_wait_prompt('vxprj vsb add IPNET_DHCPS IPNET_FIREWALL IPNET_IKE IPNET_IPSEC IPNET_RIP')
            config = ' -add '.join(['_WRS_CONFIG_COMPONENT_IPDHCPS=y',
                                    '_WRS_CONFIG_COMPONENT_IPIKE=y',
                                    '_WRS_CONFIG_COMPONENT_IPIPSEC=y',
                                    '_WRS_CONFIG_COMPONENT_IPMCP=y',
                                    '_WRS_CONFIG_COMPONENT_IPRIP=y',
                                    '_WRS_CONFIG_COMPONENT_IPFIREWALL=y',
                                    '_WRS_CONFIG_COMPONENT_FEATURE_IPNET_INET6=y'])
            self.send_and_wait_prompt('vxprj vsb config -o -add %s' % config)

        elif self.vxworks.startswith('7'):
            self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y')
            self.send_and_wait_prompt(
                'vxprj vsb add IPNET_DHCPS IPNET_FIREWALL IPNET_IKE IPNET_IPSEC IPNET_IPSECIKE IPNET_ROUTEPROTO')
        # debug for SR0600
        elif self.vxworks.startswith('platform'):
            self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y')
            self.send_and_wait_prompt(
                'vxprj vsb add IPNET_DHCPS IPNET_FIREWALL IPNET_IKE IPNET_IPSEC IPNET_IPSECIKE IPNET_ROUTEPROTO')
            # debug end for SR0600
        # added by xiaozhan for debug mode,start
        #  self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_DEBUG_FLAG=y')
        # self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_IPCOM_DEFAULT_SYSLOG_PRIORITY_DEBUG2=y')
        #  self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_IPCOM_DEBUG_SYSLOG_PRIORITY_DEBUG2=y ')
        #  self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_IPCOM_DEBUG_ADVANCED=y')
        # added by xiaozhan for debug mode,end
        elif self.vxworks.startswith('helix'):
            self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y')
            self.send_and_wait_prompt('vxprj vsb add IPNET_DHCPS IPNET_FIREWALL  IPNET_IPSECIKE IPNET_ROUTEPROTO')

        self.wait_prompt(cleanup=True)
        self.s.setmaxread(1000)
        self.s.sendline('make -j 8 2>&1')
        i = self.s.expect(['done all', self.prompt])
        if i == 0:
            print
            '\nVSB build succussfully!\n'
            if self.debug:
                print
                'vsb build -> self.s.before=%s\n' % self.s.before
                print
                'vsb build -> self.s.after=%s\n' % self.s.after
            self.s.setmaxread(1)
            self.s.expect(self.prompt)
        elif i == 1:
            print
            'vsb build -> self.s.before=%s\n' % self.s.before
            print
            'vsb build -> self.s.after=%s\n' % self.s.after
            print
            '\nError! "done all" isn\'t found. VSB build is failed!\n'
            sys.exit(1)

    def build_ANVL_suite(self, suite='', sudo=False):
        print
        "====================================================================\n"
        print
        "=========          start to build ANVL VSB...           ============\n"
        print
        "====================================================================\n"
        print
        "Processing...\n"
        self.setEnv()
        # for build script,please refer to my buidRtne.sh
        return

    def clearExpectBuffer(self):
        i = self.s.expect([self.prompt, pexpect.TIMEOUT, pexpect.EOF])
        if self.debug:
            print
            "clearExpectBuffer i = %s" % i
        if i == 1 or i == 2:
            self.send_and_wait_prompt('\x03')