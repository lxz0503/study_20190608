#############################################################################
#
# Copyright (c) 2018, 2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#

import re
import util
import subprocess
import pexpect
import socket
import time
import threading
from util import IF
import time

FUNC_RET_SUCCESS = 'value = 0 = 0x0'
bStart = False
loopCount = 2500
resultFile = "/ram0/coresafetyresult.txt"
 
def startServer (ks, rs):
    global bStart
    if bStart:
        return
    
    # run the upd server in kernel
    ks.send('C sp testStartUdpServer')
    
    rs.send('C ATestSPRTP("server", "localhost", "1000")')
    bStart = True
    
def runClient(log, cmd, c):
    log ('executing %s' % (cmd))
    ret = c.send_and_return_all(cmd)
    log ('%s result: %s' % (cmd, ret))
    
    time.sleep (90)
    
    # check the result
    cmd = 'C testGetResult'
    log ('executing %s' % (cmd))
    ret = c.send_and_return_all(cmd)
    log ('%s result: %s' % (cmd, ret))
    
    # The 'ret' has lots of other string. 
    if ret[-2] != "OK":
        raise test_fail('memory is used up')
    
    cmd = 'rm %s' % (resultFile)
    c.send (cmd)

class kernel_rtp_no_used_up:
    'Test the memory is not used up when the server is running in kernel space\
    and the client is running in user space'
    
    def config(self):
        self.hosts = 4
        self.eta = 180
        self.v6 = False
    
    def test(self, log, hosts, v6, opt):
        ks, rs, a, b = hosts
        
        startServer (ks, rs)
        
        # the client running in the user space sends data to the server
        
        cmd = 'C ATestSPRTP("client", "%s", "%s")' % (ks.ip().addr, loopCount)
        runClient (log, cmd, a)

class kernel_kernel_no_used_up:
    'Test the memory is not used up when the server is running in kernel space\
    and the client is running in kernel space'
    
    def config(self):
        self.hosts = 4
        self.eta = 180
        self.v6 = False
    
    def test(self, log, hosts, v6, opt):
        ks, rs, a, b = hosts
        
        startServer (ks, rs)
        
        # the client running in the user space sends data to the server
        
        cmd = 'C sp testStartUdpClient, "%s", %s' % (ks.ip().addr, loopCount)
        runClient (log, cmd, a)
        
class rtp_kernel_no_used_up:
    'Test the memory is not used up when the server is running in user space\
    and the client is running in kernel space'
    
    def config(self):
        self.hosts = 4
        self.eta = 180
        self.v6 = False
    
    def test(self, log, hosts, v6, opt):
        ks, rs, a, b = hosts
        
        startServer (ks, rs)
        
        # the client running in the user space sends data to the server
        
        cmd = 'C sp testStartUdpClient, "%s", %s' % (rs.ip().addr, loopCount)
        runClient (log, cmd, b)
        
class rtp_rtp_no_used_up:
    'Test the memory is not used up when the server is running in user space\
    and the client is running in user space'
    
    def config(self):
        self.hosts = 4
        self.eta = 180
        self.v6 = False
    
    def test(self, log, hosts, v6, opt):
        ks, rs, a, b = hosts
        
        startServer (ks, rs)
        
        # the client running in the user space sends data to the server
        
        cmd = 'C ATestSPRTP("client", "%s", "%s")' % (rs.ip().addr, loopCount)
        runClient (log, cmd, b)
        