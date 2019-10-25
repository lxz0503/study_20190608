import os
import sys
import pexpect
import time
from pexpect import TIMEOUT


class Telnet(object):
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
                self.t.send(os.linesep)
                self.t.expect(':')
                self.t.sendline(bootLine)
                print "the bootLine is %s" % bootLine
                self.t.expect('->',timeout=None)
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
