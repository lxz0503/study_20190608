#!/usr/bin/env python
import sys
import time
import socket

from KongUtil import runShCmd
from HelixCommon import *
#from runtestsuite_conf import testable_packages

def main_try():
    print('=== helix test')
    print(sys.argv)
    time.sleep(16)
    branch, commit, module, bsp = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    if module == 'SSH':
        sys.exit(1) 
    

def main():
    # HelixTest.py $BRANCH $NEWCOMMIT $MODULE $BSP
    # check arguments
    if len(sys.argv) != 5:
        print('\nusage:%s $BRANCH $NEWCOMMIT $MODULE $BSP')
        sys.exit(1)
    
    branch, newCommit, module, bsp = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    # set up env
    gitPath = getGitPath(branch)
    imageServer = getImageServer()
    currentServer = socket.gethostname().split('.')[0]
    if currentServer != imageServer:
        gitPath = '/net/%s/%s' % (imageServer, gitPath)
    scriptPath = getScriptPath(gitPath)
    #testCase = ','.join(testable_packages[module]['testengine_name'])
    testCase = newCommit
    # copy tar file
    tarPath = '%s/%s/%s.tar' % (getImagePath(), bsp, module)
    runShCmd('cp %s ./' % tarPath)
    runShCmd('tar zxf %s.tar' % module)
    # build - runKong.sh -g gitPath -m module -b bsp --helix
    buildCmd = '%s/runKong.sh -g %s -m %s -c %s -b %s --helix testOnly' % (scriptPath, gitPath, module, testCase, bsp)
    print('=== test cmd:%s' % buildCmd)
    retCode, ret = runShCmd(buildCmd)
    print(ret)
    print(retCode)
    # decide test pass or not
    testPass = 'Info: tinderbox: status: success'
    if ret.find(testPass) != -1:
        sys.exit(0)
    else:
        sys.exit(1)

     
if __name__ == '__main__':
    main()
