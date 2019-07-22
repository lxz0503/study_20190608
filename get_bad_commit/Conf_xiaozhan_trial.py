#!/usr/bin/env python

import getopt
import sys
import os
import pexpect
import re
import stat
import time
import traceback
from pexpect import TIMEOUT
from scp_file_test import scp_file
import shutil

class CommandlineArgumentException(Exception):
    pass
class PduStateException(Exception):
    pass

AnvlServer = {
'addr'       : "128.224.166.46",
'user'       : "root",
'passwd'     : "kernel",
'prompt'  : "root@pek-xli3-d2 ",
}

#AnvlSuiteAll = ['RipSplitHorizon','IKEv2','ICMPv4','ICMPv6','IPv4','IPv6FlowLevelEnable','IPv6FlowLevelDisable','IPGW','IGMPv2','IGMPv3','Mldv1','Mldv2','DHCPC','DHCPS','RipPoison','RipCompatibility','RipSplitHorizon','IKEIPv6Main','IPsecAHv4','IPsecAHv6','IPsecESPv4','IPsecESPv4-noencry','IPsecESPv6','IPsecESPv6-des','IKEMain','IKEAggressive','IKECombinedSA','IKEDH1md5','IKEDH1sha','IKEIPv6CombinedSA','IKEIPv6Aggressive','IKEIPv6md5']
# remove IKEMain for p1 defect
AnvlSuiteAll = ['RipSplitHorizon','RipSplitHorizon','ICMPv4','ICMPv6','IPv4','IGMPv2','IGMPv3','IPv6FlowLevelEnable','IPv6FlowLevelDisable','IPGW','Mldv1','DHCPC','DHCPS','RipPoison','RipCompatibility','IPsecAHv4','IPsecAHv6','IPsecESPv4','IPsecESPv4-noencry','IPsecESPv6','IPsecESPv6-des','IKEAggressive','IKECombinedSA','IKEDH1md5','IKEDH1sha','IKEIPv6CombinedSA','IKEIPv6Aggressive','IKEIPv6md5','RipSplitHorizon']
def HelpGuide():
    print '''\nUsage:    ./Conf.py [option...]\n\nMANDATORY OPTIONS:\n\n    -r(--run=)    ANVL\n\n    --bsp         Input BSP,ie: --bsp=pcPentium4, --bsp=itl_64_1_1_0_0\n\n    --tool        Input compiler toolchain,ie: --tool=gnu,--tool=diab\n\n    --vxworks     Input vxworks DVD version,ie: --vxworks=6.9.3.3,--vxworks=7\n\n        [--dvd    Input vxWorks DVD server info, including ssh-user, ssh-passwd, address, ssh-prompt and DVD path. For its format, see example in bottom.]\n    or\n        [-n(--nobuild=)  Input image path and platform will skip VSB/VIP build process.]\n\n    --localSSH    Input local SSH info used by DVD server to scp vxWorks image to local FTP dir. For its format, see example in bottom.\n\n    --localAddr   Input local address used by DVD server as destination to save TAHI images. For its format, see example in bottom.\n\n    --localFTP    Input local FTP info to save TAHI images. For its format, see example in bottom.\n\nOPTIONAL OPTIONS:\n\n    -s(--suite=)  Input test suite(s) and use "," to separate each suite. If this option isn\'t given , system will run all suites\n\n                  TAHI suites:\n                      | host | router | dhcpc6 | dhcps6 | dhcpr6 |\n                  ANVL suites: 
                      ICMPv4,ICMPv6,IPv4,IPv6FlowLevelEnable,IPv6FlowLevelDisable,
                      IPGW,IGMPv2,IGMPv3,Mldv1,Mldv2,DHCPC,DHCPS,
                      RipPoison,RipCompatibility,RipSplitHorizon,
                      TcpCore_UrgPtrRFC1122,TcpCore_UrgPtrRFC793,TcpAdv,TcpPerf,
                      IPsecAHv4,IPsecAHv6,IPsecESPv4,IPsecESPv4-noencry,IPsecESPv6,IPsecESPv6-des,
                      IKEMain,IKEAggressive,IKECombinedSA,IKEDH1md5,IKEDH1sha,IKEv2,
                      IKEIPv6Main,IKEIPv6CombinedSA,IKEIPv6Aggressive,IKEIPv6md5\n\n    -c(--case=)  Input case(s) to test. This option only support ANVL now.\n                 If this option isn\'t given , system will run all suites. Valid format is as below:\n\n                 individual number    e.g. 2.3\n                 group number     e.g. 2\n                 range of numbers     e.g. 1.1-1.5 or 1-3\n                 wildcard use     e.g. 1-* or 2.3-2.*\n                 multiple numbers     e.g  1.1, 2.3, 6.3\n\n    --log=       Input log folder fullpath that you want to save your log, if not given, system will create log folder with timestamp under current directory.\n\n    --merge      If not this option, system will create log folder with timestamp under dir identified by "--log". If given, system will save case log into folder identified by "--log" directly.\n\n    --exclude=   Remove suite(s) from executable suite(s) that indicated by "--suite" option or all suites if no "--suite" option.\n\n    --debug      Enable debug mode,default is disabled\n\nEXAMPLES:  \n\n    ./Conf.py -r ANVL --dvd="dvdUser=windriver,dvdPwd=windriver,dvdAddr=128.224.166.223,dvdPrompt=windriver@Nightly-testServer01:,dvdPath=/home/windriver/DVD_Installation/Nightly/vx20151224084202_vx7-SR0440-V2-features_vx7-release" --bsp=itl_64_vx7 --tool=gnu --vxworks=7 --localFTP="ftpuser=target,ftppwd=target,ftpdir=/tftproot" --localSSH="sshuser=root,sshpwd=rootroot" --localAddr="128.224.162.211"  --log=/tftproot --target="console=128.224.164.57 2016,pduAddr=128.224.164.113,pduPort=6,bootEth=gei,bootPort=2,bootIp=128.224.166.238:0xfffffe00" --nobuild=/tftproot/Vx7/Dec/vxWorks  -s ICMPv4 -c 1.1 --debug\n'''


class _dummy:
    def setlog(*_):
        pass

class telnet(object):
    '''operates on a baselinux
    Expects passwordless sudo unless logged in as root.'''
    def __init__(self):
        print ">>>>>>>>>     start to boot target...       <<<<<<<<\n"
        self.type = 'telnet'
        self.t = _dummy()

    def statusCheck(self, addr):
        cmdTelnet = 'telnet %s'%addr
        self.t = pexpect.spawn(cmdTelnet)
        self.t.send(os.linesep)
        i = self.t.expect(['VxWorks Boot]:', '->', 'Press any key to stop auto-boot...', pexpect.TIMEOUT, pexpect.EOF], 1000)            
        if i != 0:
            print "ERROR! You must make sure ANVL DUT is under [VxWorks Boot]: shell before automation testing."
            sys.exit(1)     

    def bootTarget(self,  addr, bootLine):
        cmdTelnet = 'telnet %s'%addr
        self.t = pexpect.spawn(cmdTelnet)
        self.t.send(os.linesep)
        for _ in range(10):
            i = self.t.expect(['VxWorks Boot]:', 
                               '->', 
                               'Press any key to stop auto-boot...', 
                               pexpect.TIMEOUT, 
                               pexpect.EOF], 1000)  
            print "i=%s\n"%i            
            if i == 0:    
                self.t.sendline(bootLine)
                print "the bootLine is %s" % bootLine
                time.sleep(20)
                self.t.expect('->') 
                print self.t.before 
                print self.t.after 
                print "\nANVL target boot up successfully!\n"
                break
            
            if i == 1: 
#debug by xiaozhan
                self.t.sendline('reboot')
                self.t.expect('vxTarget')
                print "the output is %s" % self.t.before
                print "the output is %s" % self.t.after
                self.t.send(os.linesep)
                self.t.expect(':')
                print "the output is %s" % self.t.before
                print "the output is %s" % self.t.after
                self.t.sendline(bootLine)
                print "the bootLine is %s" % bootLine
                self.t.expect('->',timeout=None)
                print "the  output is %s" % self.t.before
                print "the  output is %s" % self.t.after
                print "\nANVL target boot up successfully!\n"
                break
#debug by xiaozhan
            if i == 2:      
                self.t.send(os.linesep)
                continue
                
            if i == 3 or i == 4:      
                print self.t.before
                print 'ERROR!: port server "%s" is not connective!\n'%cmdTelnet
                sys.exit(1)
                

    #xiaozhan, there is something wrong with the terminal server and it can not quit console session
    def logout(self):
        self.t.sendline('\x1d')
        self.t.expect('telnet>')
        self.t.sendline('q')           
        self.t.expect([pexpect.EOF, pexpect.TIMEOUT])
        print self.t.before, self.t.after
        time.sleep(2)
        print ">>>>>>>>>    boot target done!       <<<<<<<<\n"

class pduControl(object):
    '''VLM pdu control'''
    def __init__(self, addr, port):
        print ">>>>>>>>>     start to power down/up target by pdu...       <<<<<<<<\n"
        self.type = 'telnet'
        t = _dummy()
        self.port = port
        cmdTelnet = 'telnet '+ addr
        t = pexpect.spawn(cmdTelnet)
        t.send(os.linesep)
        i = t.expect(['User Name :' , 'Connection closed by foreign host', pexpect.TIMEOUT, pexpect.EOF])
        self.t = t  
        print "i=%s\n"%i 
        print "t.before=%s\n"%self.t.before
        print "t.after=%s\n"%self.t.after           
        if i == 0:
            print "go here?"     
            #time.sleep(1)
            userName = "apc"
            self.t.sendline(userName)
            time.sleep(2)
            t.expect('Password  :') 
            print "t.before=%s\n"%self.t.before
            print "t.after=%s\n"%self.t.after
            self.t.sendline('apc -c\n')
            self.t.expect('APC>') 
            print "t.before=%s"%self.t.before
            print "t.after=%s"%self.t.after        
        elif i == 1: 
            raise PduStateException("pdu %s %s is busy now!\n"%(addr, port))
        else:           
            raise PduStateException("pdu %s %s isn't connective now!\n"%(addr, port))            

    def powerOn(self):
        print "go powerOn" 
        time.sleep(1)
        self.t.sendline('on '+ self.port)
        self.t.expect('APC>')
        print "t.before=%s\n"%self.t.before
        print "t.after=%s\n"%self.t.after
        time.sleep(180)
        
    def powerOff(self):
        print "go powerOff" 
        time.sleep(1)
        self.t.sendline('off '+ self.port)
        self.t.expect('APC>')  
        print "t.before=%s\n"%self.t.before
        print "t.after=%s\n"%self.t.after
        
    def reboot(self):
        print "go reboot"     
        self.powerOff()
        self.powerOn()
        print ">>>>>>>>>     power down/up target is done!        <<<<<<<<\n"
        
    def logout(self):
        self.t.sendline('\x1d')
        self.t.expect('telnet>')
        self.t.sendline('q')           
        self.t.expect([pexpect.EOF, pexpect.TIMEOUT])    
            
class ssh(object):
    '''operates on a baselinux
    Expects passwordless sudo unless logged in as root.'''
    def __init__(self, opt):
        self.type = 'ssh'
        self.opt = opt
        self.prompt = self.opt['dvdPrompt']
        self.env = False
        #if self.opt.has_key('debug'):    
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
        cmdSSH = 'ssh %s@%s'%(self.opt['dvdUser'], self.opt['dvdAddr'])
        if self.debug:
            print "ssh cmdSSH=%s\n"%cmdSSH
        s = pexpect.spawn(cmdSSH)
        for _ in range(2):
            i = s.expect([self.opt['dvdPrompt'],
                                 'assword:',
                                 'Are you sure you want to continue connecting',
                                 pexpect.TIMEOUT,
                                 pexpect.EOF]) 
            if self.debug:
                print "ssh i=%s\n"%i
                print "s.before=%s\n"%s.before
                print "s.after=%s\n"%s.after
            if i == 2:
                s.sendline('yes')
            if i == 1:
                s.sendline(self.opt['dvdPwd'])
                s.expect(self.opt['dvdPrompt'])
                if self.debug:
                    print "s.sendline(self.opt['dvdPwd'])-> s.before=%s\n"%s.before
                    print "s.sendline(self.opt['dvdPwd'])-> s.after=%s\n"%s.after
                break
            if i == 0:
                break
            if i == 3 or i == 4:
                print "ERROR!: cannot ssh to server %s!\n"%self.opt['dvdAddr']
                sys.exit(1)
        #cguo: no need to set prompt due to it is destroyed after vxWorks wrenv.linux                 
        #cmdSetPrompt = 'export PS1="'+self.prompt+'"'
        #s.sendline(cmdSetPrompt)
        self.s = s
        self.wait_prompt(cleanup = True)
                
    def backup_src_file(self, filefullpath, sudo = False):
        if self.debug:
            print "goto backup_src_file\n"                                         
        if sudo:    
            backup_cmd = "sudo cp " + filefullpath + " " + filefullpath +".bak"
        else:    
            backup_cmd = "cp " + filefullpath + " " + filefullpath +".bak"
        self.wait_prompt(cleanup = True)
        self.s.sendline('ls ' + filefullpath +'.bak')            
        i = self.s.expect(['No such file', self.prompt])   
        if self.debug:
            print "goto backup_src_file i=%s\n"%i
            self.printExpectInfo('ls ' + filefullpath +'.bak')              
        if i == 1:
            self.s.sendline("cp -f " + filefullpath +".bak" + " " + filefullpath )   
            j = self.s.expect(['\?', self.prompt])           
            if self.debug:
                print "goto backup_src_file j=%s\n"%j 
                self.printExpectInfo("cp -f" + filefullpath +".bak" + " " + filefullpath)
            if j == 0:  
                self.send_and_wait_prompt('y')
            return   

        self.s.expect(self.prompt)
        self.wait_prompt(cleanup = True)
        self.s.sendline(backup_cmd)
        i = self.s.expect(['\?', self.prompt])
        if self.debug:
            self.printExpectInfo(backup_cmd)
        if i == 0:
            self.send_and_wait_prompt('n') #If origin .bak is existing, the origin one should be useful
            self.send_and_wait_prompt("cp -f " + filefullpath +".bak" + " " + filefullpath )
            self.send_and_wait_prompt('y')                                              
        self.wait_prompt(cleanup = True)

    def recover_src_file(self, bakFile, sudo = False):
        if self.debug:
            print "goto recover_src_file\n"
        oriFile = bakFile.split('.bak')[0]
        self.wait_prompt(cleanup = True)
        self.s.sendline('ls ' + bakFile)            
        i = self.s.expect(['No such file', self.prompt])            
        if self.debug:
            self.printExpectInfo('ls ' + bakFile)
        if i == 0:
            print 'ERROR!: the bak file "%s" used to recover is nonexistent!\n'%bakFile   
        self.wait_prompt(cleanup = True)
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
        self.wait_prompt(cleanup = True)
          
    def modify_src_file(self, fileDir, fileName, CurCode, NewCode, sudo = False): 
        if self.debug:
            print "goto modify_src_file\n"
        fileFullPath = fileDir + fileName
        cloneFilePath = fileDir + "clone.txt"
        
        if sudo:        
            cmdClone = "sudo mv " + fileFullPath+" " + cloneFilePath
        else:
            cmdClone = "mv " + fileFullPath+" " + cloneFilePath       
        self.s.sendline(cmdClone)
        i = self.s.expect(['\?', self.prompt])
        if self.debug:
            self.printExpectInfo(cmdClone)
        if i == 0:
            self.send_and_wait_prompt('y')
             
        self.wait_prompt(cleanup = True)
        if sudo:        
            cmdSed = "sudo sed 's/"+CurCode+"/"+NewCode+"/g' "+cloneFilePath+" > "+fileFullPath
        else:
            cmdSed = "sed 's/"+CurCode+"/"+NewCode+"/g' "+cloneFilePath+" > "+fileFullPath      
        self.send_and_wait_prompt(cmdSed)
        
        if sudo:        
            cmdRmClone = "sudo rm -f "+cloneFilePath
        else:
            cmdRmClone = "rm -f "+cloneFilePath        
        self.send_and_wait_prompt(cmdRmClone)
 
    def setEnv(self):
        if self.debug:
            print "goto setEnv\n" 
            print "the dvdpath is %s" %self.dvdpath
        if self.env:
            return
        self.send_and_wait_prompt('cd '+ self.dvdpath) 
        if self.vxworks.startswith('7') or self.vxworks.startswith('platform'):
		
#if 6,7 or platform,run below command
            self.send_and_wait_prompt('./wrenv.linux -p vxworks-' + self.vxworks) 
        elif self.vxworks.startswith('helix'):			
#if it is for vx7-integration,then it should be helix,run below command
            self.send_and_wait_prompt('./wrenv.linux -p helix')
        else:
            print "wrong vxworks!"
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
        print "[%s] --> self.s.before='%s'\n"%(cmd, self.s.before) 
        print "[%s] --> self.s.after='%s'\n"%(cmd, self.s.after)

    def send_and_wait_prompt(self, cmd, timeout = -1):
        self.s.sendline(cmd)
        self.wait_prompt(timeout)
        if self.debug:
            self.printExpectInfo(cmd)
        self.wait_prompt(cleanup = True)
        
    def wait_prompt(self, timeout = -1, cleanup = False):
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
                print "wait_prompt clean -> get pexpect.TIMEOUT\n"
                raise

        except pexpect.EOF:
            if not cleanup:
                print "wait_prompt clean -> get pexpect.EOF\n"
                raise
                                            
    def transfer_file(self, src, dst, passwd):
        if self.debug:
            print "goto transfer_file"
        self.s.sendline('scp %s %s '%(src, dst))       
        for _ in range(2):
            i = self.s.expect(['assword:', 'Are you sure you want to continue connecting',pexpect.TIMEOUT]) 
            if self.debug:
                self.printExpectInfo('scp %s %s '%(src, dst))
                print "transfer_file: i=%d\n"%i
            if i == 1:
                self.s.sendline('yes')
            if i == 0:
                self.s.sendline(passwd)
                self.s.expect(self.prompt)
                break
            if i == 2:
                print "copy log timeout!"
                break
                
    def transfer_folder(self, src, dst, passwd):
        self.s.sendline('scp -q -r %s %s '%(src, dst))       
        for _ in range(2):
            i = self.s.expect(['assword:','Are you sure you want to continue connecting']) 
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
        self.wait_prompt(cleanup = True)
        self.s.sendline('ls default/vxWorks') 
        i = self.s.expect(['No such file',self.prompt]) 
        if self.debug:
            print 'ls default/vxWorks -> self.s.before=%s\n'%self.s.before
            print 'ls default/vxWorks -> self.s.after=%s\n'%self.s.after
        if i == 0:
            print 'ERROR!: VIP build failed!\n'
            sys.exit(1)
        if i == 1:
            print 'VIP build succussfully!\n'
        
    def setSharedWorkspace(self, sudo = False):
        if self.debug:
            print "goto setSharedWorkspace\n"
        if not self.sharedWorkspace:  
            FolderPath = self.dvdpath + "/%sBuild-"%(self.confRun)+ curTime  
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
            self.send_and_wait_prompt(cmdChmod )
            self.sharedWorkspace = FolderPath
            if self.confRun == 'ANVL':            
                self.dstImageFolder = self.opt['ftpdir'] + '/%s_%s_'%(self.confRun, self.vxworks)+curTime
            else:
                print 'ERROR! You input invalid type "%s" with "-r(--run)". The valid is ANVL / TAHI\n'%self.confRun
                sys.exit(1) 
        else:
            return

    def vsb_create_and_build(self, suite):
        if self.debug:
            print "goto vsb create\n"
        if self.confRun == 'ANVL':     
            #self.transfer_file(self.opt['sshuser']+'@'+self.opt['localAddr']+':'+self.opt['pwd']+'/'+self.confRun+'_vsbcfg/'+'Vx'+(self.vxworks).split('.')[0]+'/vsb.config', self.sharedWorkspace, self.opt['sshpwd'])    
            self.vsbDir = self.sharedWorkspace+'/VSB_%s'%(self.confRun)
            # =====add this parameter -inet for vx6,the default configuration for vx6 is IPv4. For vx7 the default configuraiton is IPv4 and IPv6.  xiaozhan =====#
            self.send_and_wait_prompt('vxprj vsb create -S -lp64 -cpu CORE -smp -inet6 -profile DEVELOPMENT -bsp %s  %s'%(self.bsp, self.vsbDir), timeout = 60)
         
        else:
            print 'ERROR! You input invalid type "%s" with "-r(--run)". The valid is ANVL / TAHI \n'%self.confRun
            sys.exit(1)             
        if self.debug:
            print "goto vsb build\n"
      #debug by xiaozhan,add \n
        self.send_and_wait_prompt('cd '+self.vsbDir + '\n')
        if self.vxworks.startswith('6'):
            #self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y')
            #self.send_and_wait_prompt('vxprj vsb add IPNET_DHCPS IPNET_FIREWALL IPNET_IKE IPNET_IPSEC IPNET_RIP')
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
            self.send_and_wait_prompt('vxprj vsb add IPNET_DHCPS IPNET_FIREWALL IPNET_IKE IPNET_IPSEC IPNET_IPSECIKE IPNET_ROUTEPROTO')
         #debug for SR0600
        elif self.vxworks.startswith('platform'):
             self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y')
             self.send_and_wait_prompt('vxprj vsb add IPNET_DHCPS IPNET_FIREWALL IPNET_IKE IPNET_IPSEC IPNET_IPSECIKE IPNET_ROUTEPROTO')
             #debug end for SR0600
            #added by xiaozhan for debug mode,start
          #  self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_DEBUG_FLAG=y')
           # self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_IPCOM_DEFAULT_SYSLOG_PRIORITY_DEBUG2=y')
          #  self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_IPCOM_DEBUG_SYSLOG_PRIORITY_DEBUG2=y ')
          #  self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_IPCOM_DEBUG_ADVANCED=y') 
            #added by xiaozhan for debug mode,end
        elif self.vxworks.startswith('helix'):
            self.send_and_wait_prompt('vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y')
            self.send_and_wait_prompt('vxprj vsb add IPNET_DHCPS IPNET_FIREWALL  IPNET_IPSECIKE IPNET_ROUTEPROTO')

        self.wait_prompt(cleanup = True)
        self.s.setmaxread(1000)
        self.s.sendline('make -j 8 2>&1')
        i = self.s.expect(['done all', self.prompt]) 
        if i == 0:
            print '\nVSB build succussfully!\n'
            if self.debug:
                print 'vsb build -> self.s.before=%s\n'%self.s.before
                print 'vsb build -> self.s.after=%s\n'%self.s.after
            self.s.setmaxread(1)
            self.s.expect(self.prompt) 
        elif i == 1:
            print 'vsb build -> self.s.before=%s\n'%self.s.before
            print 'vsb build -> self.s.after=%s\n'%self.s.after
            print '\nError! "done all" isn\'t found. VSB build is failed!\n'
            sys.exit(1)            

    def build_ANVL_suite(self, suite= '', sudo = False):
        print "====================================================================\n"
        print "=========          start to build ANVL VSB...           ============\n"
        print "====================================================================\n"
        print "Processing...\n"
        self.setEnv()        
#for build script,please refer to my buidRtne.sh
        return
      
    def clearExpectBuffer(self):
        i = self.s.expect([self.prompt, pexpect.TIMEOUT, pexpect.EOF])
        if self.debug:
            print "clearExpectBuffer i = %s"%i
        if i == 1 or i == 2 :
            self.send_and_wait_prompt('\x03')             
                                                  
def splitDvdOption(para, arg):
    lines = arg.split(',')
    for line in lines:
        elem = line.split('=', 1)
        if len(elem) == 2:
            if elem[0] not in ('dvdUser', 'dvdPwd', 'dvdAddr', 'dvdPrompt', 'dvdPath'): 
                raise CommandlineArgumentException('%s was erronously formatted' % line)
            if not elem[1]:
                raise CommandlineArgumentException('%s was erronously formatted' % line)
            para[elem[0]] = elem[1]
        else:
            raise CommandlineArgumentException('%s was erronously formatted' % line)

def splitFtpOption(para, arg):
    lines = arg.split(',')
    for line in lines:
        elem = line.split('=', 1)
        if len(elem) == 2:
            if elem[0] not in ('ftpuser', 'ftppwd', 'ftpdir'): 
                raise CommandlineArgumentException('%s was erronously formatted' % line)
            if not elem[1]:
                raise CommandlineArgumentException('%s was erronously formatted' % line)                
            if elem[0] == 'ftpdir':
                para[elem[0]] = os.path.abspath(elem[1])
            else:
                para[elem[0]] = elem[1]
        else:
            raise CommandlineArgumentException('%s was erronously formatted' % line)

def splitSshOption(para, arg):
    lines = arg.split(',')
    for line in lines:
        elem = line.split('=', 1)
        if len(elem) == 2:
            if elem[0] not in ('sshuser', 'sshpwd'): 
                raise CommandlineArgumentException('%s was erronously formatted' % line)
            if not elem[1]:
                raise CommandlineArgumentException('%s was erronously formatted' % line)
            para[elem[0]] = elem[1]
        else:
            raise CommandlineArgumentException('%s was erronously formatted' % line)


                                    
def parseOption(argv):
    para = {
          'run'                 : '',     
          'suite'               : [],         
          'dvdUser'             : '',
          'dvdPwd'              : '',
          'dvdAddr'             : '',
          'dvdPrompt'           : '',     
          'dvdPath'             : '',
          'vxworks'             : '',
          'nobuild'             : '',  
          'bsp'                 : '', 
          'tool'                : '', 
          'debug'               : False, 
          'log'                 : '',
          'ftpuser'             : '', 
          'ftppwd'              : '',           
          'ftpdir'              : '',              
          'sshuser'             : '',   
          'sshpwd'              : '', 
          'localAddr'           : '',  
          'pwd'                 : '',
          'merge'               : False, 
          'case'                : '',
          'exclude'             : [],
          'console'             : '',
          'pduAddr'             : '',
          'pduPort'             : '',
          'bootEth'             : '',
          'bootPort'            : '',
          'bootIp'              : '',
          }
    para['pwd'] = os.path.abspath(os.getcwd())
    shorts = 'r:s:n:c:t:'
    longs = ['run=','suite=','dvd=','vxworks=','nobuild=','bsp=','tool=','result=','log=','localFTP=','localAddr=','localSSH=','result=','exclude=','case=','target=','debug','help','merge']
    try:
        opts, args = getopt.gnu_getopt(argv, shorts, longs)
    except getopt.GetoptError, desc:
        print 'ERROR! %s!\n'%desc
        sys.exit(1)
    if args:
        print 'ERROR! You input invalid format %s!\n'%args
        sys.exit(1)
    for opt, arg in opts:
        if opt in ('--help'):
            HelpGuide()
            sys.exit(1)
        if opt in ('-r', '--run'):
            if arg == 'ANVL':
                para['run'] = arg  
                continue
            else: 
                print 'ERROR! You input invalid type "%s" with "-r(--run)". The valid is ANVL\n'%arg
                sys.exit(1)
        elif opt in ('-s', '--suite'):
            List = arg.split(',') 
            if 'all' in List:
                para['suite'] = AnvlSuiteAll
            else:
                para['suite'] = List    
            continue        
           
        elif opt in ('-t', '--target'):
            List = arg.split(',') 
            for subOpt in List:
                para[subOpt.split('=')[0]] = subOpt.split('=')[1]                  
            continue 
            
        elif opt in ('--exclude',):
            para['exclude'] = arg.split(',') 
            continue
        elif opt in ('--dvd',):
            splitDvdOption(para, arg)
            continue
        elif opt in ('--localFTP',):
            splitFtpOption(para, arg)
            continue
        elif opt in ('--localSSH',):
            splitSshOption(para, arg)
            continue
        elif opt in ('--localAddr',):
            para['localAddr'] = arg
            continue
        elif opt in ('--bsp',):
            para['bsp'] = arg
            continue
        elif opt in ('--tool',):
            para['tool'] = arg
            continue
        elif opt in ('--log',):
            para['log'] = os.path.abspath(arg)
            continue
        elif opt in ('--merge',):
            para['merge'] = True
            continue
        elif opt in ('--vxworks',):
            tmpArg = arg.split('.')[0]
            if tmpArg not in ('6', '7','platform','helix'):
                raise CommandlineArgumentException('--vxworks=%s was erronously formatted' % arg)    
            if tmpArg == '6':
                assert len(arg.split('.')) > 1
                tmpArg = arg.split('.')[0]+'.'+arg.split('.')[1]
            para['vxworks'] = tmpArg
            continue
        elif opt in ('-c', '--case'):
            para['case'] = arg
            continue
        elif opt in ('--debug',):
            para['debug'] = True
            continue
        elif opt in ('-n', '--nobuild'):
            para['nobuild'] = os.path.abspath(arg)
            continue
        else:
            print 'ERROR!: You input invalid option "%s"\n'%opt
            HelpGuide()
            sys.exit(1)  
    if not para['run']:
        print"ERROR! You don't input test type with '-r' or '--run'. The valid one is ANVL\n" 
        sys.exit(1)                     
    if not para['vxworks']:
        print"ERROR! You don't input vxworks DVD version with '--vxworks'. The valid ones are 6.9.3.3 / 7 / platform ..." 
        sys.exit(1) 
    if not para['bsp']:
        print"ERROR! You don't input bsp to indicate target type with '--bsp'.\n"               
        sys.exit(1)
    if not para['tool']:
        print"ERROR! You don't input compiler toolchain with '--tool'.\n"               
        sys.exit(1)
    if not para['dvdUser'] and not para['nobuild']:
        print"ERROR! You don't input --dvd or --nobuild. Execute \"./Conf.py\" for help.\n"               
        sys.exit(1)
        
    if not para['ftpuser']:
        print"ERROR! You don't input local FTP info to save ANVL images with '--localFTP'. Execute \"./Conf.py\" for help.\n"               
        sys.exit(1)
    if not para['sshuser']:            
        print"ERROR! You don't input local SSH info used by DVD server to scp vxWorks image to local FTP dir with '--localFTP'. Execute \"./Conf.py\" for help.\n"               
        sys.exit(1)            
    if not para['localAddr']: 
        print"ERROR! You don't input local address used by DVD server as destination to save ANVL images. Execute \"./Conf.py\" for help.\n"               
        sys.exit(1)
    #if not para['case']:
        #print "ERROR! You don't input test case info to be run with '-c(--case=)'.Execute \"./Conf.py\" for help.\n"
        #sys.exit(1)
    #if not para['suite']:
        #print "ERROR! You don't input test suite info to be run with '-s(--suite=)'.Execute \"./Conf.py\" for help.\n"
        #sys.exit(1)
    if not para['console']:
        print "ERROR! You don't input ANVL DUT info to be run with '-s(--target=)'.Execute \"./Conf.py\" for help.\n"
        sys.exit(1)   


    return para, args   

if __name__ == '__main__':

    if len(sys.argv) == 1:
        HelpGuide()
        sys.exit(1)
    curTime = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())
    try:
        opt, tmp = parseOption(sys.argv[1:])
        if opt['debug']:
            print '\n%s\n'%opt                                                      
        # ===============modify line 772 to use itl_ to support Q35 but now pcPentium4,  ============ #
        # ==============you had better use the full name of bsp,xiaozhan ============= #
        if opt['run'] == 'ANVL':
            if not ((opt['vxworks'] == '7' and len(opt['bsp'].split('itl_')) > 1) or (opt['vxworks'] == 'platform' and len(opt['bsp'].split('itl_')) > 1) or (opt['vxworks'] == 'helix' and len(opt['bsp'].split('itl_')) > 1) or (opt['vxworks'].split('.')[0] == '6' and len(opt['bsp'].split('itl_')) > 1)):
                print 'ERROR! You input invalid or unsupported --bsp="%s" with --vxWorks="%s"\n'%(opt['bsp'],opt['vxworks'])   
                sys.exit(1)    
                      
            if opt['suite']:
                for i in opt['suite']:
                    if i not in AnvlSuiteAll:
                        print "ERROR! You input invalid ANVL suite '%s' with -s \n Valid suite is %s\n"%(i, AnvlSuiteAll)
                        sys.exit(1)
            else:
                opt['suite'] = AnvlSuiteAll
            #debug by xiaozhan,SR0600,end
            if not opt['nobuild']:
                imagePath = "/home/windriver/SPIN/vip_itl_generic/default/vxWorks"
		    #debug by xiaozhan end
            else:
                imagePath = opt['nobuild']
            print "\n====================================================================\n"
            print '===========      start to boot ANVL Target "%s"...==\n'%opt['bsp']
            print "====================================================================\n"
            
            logfolder = ''
            logfolderAlreadyCreate = False
            bootAnvlTarget = telnet()
            bootAnvlTarget.bootTarget(opt['console'], '$%s(%s,0) host:%s e=%s h=%s g=128.224.166.1 u=%s pw=%s f=0x04 '%(opt['bootEth'], opt['bootPort'], imagePath, opt['bootIp'], opt['localAddr'], opt['ftpuser'], opt['ftppwd']))
            os.system("sudo kill -9 `ps -ef | grep 128.224.164.57 | grep --color=auto telnet |  awk '{print $2}'`")
            for suite in opt['suite']:
                if suite in ['IKEv2','IKEIPv6Main']:
                    bootAnvlTarget = telnet()
                    bootAnvlTarget.bootTarget(opt['console'], '$%s(%s,0) host:%s e=%s h=%s g=128.224.166.1 u=%s pw=%s f=0x04 '%(opt['bootEth'], opt['bootPort'], imagePath, opt['bootIp'], opt['localAddr'], opt['ftpuser'], opt['ftppwd']))
                    os.system("sudo kill -9 `ps -ef | grep 128.224.164.57 | grep --color=auto telnet |  awk '{print $2}'`")
                if not logfolder:
                    if opt['log']:
                        if not opt['merge']:
                            logfolder = opt['log'] + '/ANVL_Vx'+opt['vxworks']+'_'+curTime
                        else:
                            logfolder = opt['log']
                    else:
                        logfolder = opt['pwd'] + '/ANVL_Vx'+opt['vxworks']+'_'+curTime 
                if not logfolderAlreadyCreate:                 
                    os.popen('mkdir '+logfolder)
                    logfolderAlreadyCreate = True
                opt['dvdAddr'] = AnvlServer['addr']                        
                opt['dvdUser'] = AnvlServer['user']  
                opt['dvdPwd'] = AnvlServer['passwd']  
                opt['dvdPrompt'] = AnvlServer['prompt'] 
                if len(opt['bsp'].split('itl_')) > 1:
                    opt['bsp'] = 'Q35'
                AnvlLogFolder = 'ANVL_Vx'+opt['vxworks']+'_'+curTime
                sshToAnvlServer = ssh(opt)
                sshToAnvlServer.send_and_wait_prompt('cd /root/ANVL-automation')
                print '\n<<<<<<<<<<     start to execute ANVL suite "%s"     >>>>>>>>\n'%suite
                sshToAnvlServer.s.timeout = 30000
                sshToAnvlServer.s.sendline('./ANVL.py -t %s -c all -s %s -l %s -v %s 2>&1 | tee anvl.log'%(opt['bsp'], suite, AnvlLogFolder, opt['vxworks'])) 
                j = sshToAnvlServer.s.expect([sshToAnvlServer.prompt, 'Press return and reboot DUT:'])
                if j == 0:
                    sshToAnvlServer.s.timeout = 30
                    print '<<<<<<<<<<     finish executing ANVL suite "%s"     >>>>>>>>\n'%suite
                    sshToAnvlServer.transfer_file(AnvlLogFolder+'/*.log', opt['sshuser']+'@'+opt['localAddr']+':'+logfolder, opt['sshpwd'])
                    os.system("sudo kill -9 `ps -ef | grep 128.224.166.46 | grep --color=auto ssh |  awk '{print $2}'`")
                    os.system("sudo kill -9 `ps -ef | grep 128.224.166.46 | grep --color=auto ssh |  awk '{print $2}'`")
                if j == 1:
                    print "\nbefore is %s" % sshToAnvlServer.s.before
                    print "\nafter is %s" % sshToAnvlServer.s.after
                    print '\nException! ANVL suite "%s" get target died!\n'%suite
                    os.system("sudo kill -9 `ps -ef | grep 128.224.166.46 | grep --color=auto ssh |  awk '{print $2}'`")
                    os.system("sudo kill -9 `ps -ef | grep 128.224.166.46 | grep --color=auto ssh |  awk '{print $2}'`")
                    print "\nxiaozhan debug to  rerun test suite %s and reload image\n" %suite
                    bootAnvlTarget = telnet()
                    bootAnvlTarget.bootTarget(opt['console'], '$%s(%s,0) host:%s e=%s h=%s g=128.224.166.1 u=%s pw=%s f=0x04 '%(opt['bootEth'], opt['bootPort'], imagePath, opt['bootIp'], opt['localAddr'], opt['ftpuser'], opt['ftppwd']))
                    os.system("sudo kill -9 `ps -ef | grep 128.224.164.57 | grep --color=auto telnet |  awk '{print $2}'`")
                    os.system("sudo kill -9 `ps -ef | grep 128.224.164.57 | grep --color=auto telnet |  awk '{print $2}'`")
                    sshToAnvlServer = ssh(opt)
                    sshToAnvlServer.send_and_wait_prompt('cd /root/ANVL-automation')
                    sshToAnvlServer.s.timeout = 30000
                    sshToAnvlServer.s.sendline('./ANVL.py -t %s -c all -s %s -l %s -v %s 2>&1 | tee anvl.log'%(opt['bsp'], suite, AnvlLogFolder, opt['vxworks']))
                    k = sshToAnvlServer.s.expect([sshToAnvlServer.prompt, 'Press return and reboot DUT:'])
                    if k == 0:
                        sshToAnvlServer.s.timeout = 30
                        print "\n======rerun  suite %s ok=====\n" % suite
                        sshToAnvlServer.transfer_file(AnvlLogFolder+'/*.log', opt['sshuser']+'@'+opt['localAddr']+':'+logfolder, opt['sshpwd'])
                        os.system("sudo kill -9 `ps -ef | grep 128.224.166.46 | grep --color=auto ssh |  awk '{print $2}'`")
                    if k == 1:
                        sshToAnvlServer.s.timeout = 30
                        print "=====rerun suite %s failed======" % suite
                        sshToAnvlServer.transfer_file(AnvlLogFolder+'/*.log', opt['sshuser']+'@'+opt['localAddr']+':'+logfolder, opt['sshpwd'])
                        os.system("sudo kill -9 `ps -ef | grep 128.224.166.46 | grep --color=auto ssh |  awk '{print $2}'`")
        else:
            print 'ERROR! You input invalid type "%s" with "-r(--run)". The valid is "ANVL"\n'%opt['run'] 
            sys.exit(1)  
             
    except CommandlineArgumentException, desc:
        print "%s exception raised: %s" % (desc.__class__.__name__, desc)  

    except PduStateException, desc:
        print "%s exception raised: %s" % (desc.__class__.__name__, desc)  
                   
    except Exception as eix:
        traceback.print_exc()
        print Exception,":",eix
