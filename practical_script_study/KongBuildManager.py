#!/usr/bin/env python

import os
import sys
import time
from pexpect import pxssh

from KongUtil import runShCmd
from KongConfig import kongBuildServers, kongBuildFirstFlag, kongUser, kongPassword, GetImageServer
import KongBuild

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
import paramiko
from paramiko import SSHClient

from InstallKongPatch import CopyWorkAroundFile as CopyWorkAroundFile4Git
from InstallKongPatch import CopyKongTestCasePatch as CopyKongTestCasePatch4Git

envCmds = {'pek-sec-kong-02' : 'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin:/sbin/:/usr/local/bin:/usr/bin:/usr/atria/bin:/folk/cm/bin:/folk/qms/tools:/folk/vlm/commandline:/usr/X11R6/bin:/folk/vlm/bin',
           'pek-vx-nightly3' : 'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/atria/bin',
          }

class SSH(object):
    def __init__(self, hostName, user, password):
        self.hostName = hostName
        self.user = user
        self.password = password
        self.s = None

    def Connect(self):
        try:
            s = pxssh.pxssh(timeout=60*10) # set up a long timer for setup-tools command
            s.login(server = self.hostName, username = self.user, password = self.password)
            self.s = s
        except pxssh.ExceptionPxssh as e:
            print("pxssh failed on login.")
            print(e)
            
    def Disconnect(self):
        self.s.logout()
        
    def SendCmd(self, cmd):
        if self.s is not None:
            self.s.sendline(cmd)
            self.s.prompt()
            print (self.s.before)
            return self.s.before
            

def IsSetupTool(gitStatusOutput):
    lines = gitStatusOutput.split('\n')
    for line in lines:
        if line.find(' M ') != -1: # this is the output of "git status --porcelain" so " M " is the keyword
            return True
    return False
    

def runRemoteCmd(client, cmd, prefix=None, showOutput=True):
    if prefix is not None:
        cmd = '%s ; %s' % (prefix, cmd)
    # add "echo $?" as workaround to get the executing status of a remote command
    cmd += ' ; echo $?'
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read()
    err = stderr.read()
    retCode = out.strip().split(os.linesep)[-1].strip()
    if retCode != '0':
        raise Exception('ERROR happen when running the command below:\n' + \
                        'cmd=%s\n' % cmd + \
                        'stdout=%s\n' % out + \
                        'stderr=%s\n' % err)
    if showOutput:
        print('\ncmd=%s' % cmd) 
        print('output=%s' % out)
    return out

    
def HandleBranch(branch, commit):
    returnCode = 0
    if kongBuildFirstFlag:
        for node in kongBuildServers:
            if node != 'pek-vx-nightly31':
                try:
                    client = SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(node, username=kongUser, password=kongPassword)

                    gitPath = kongBuildServers[node]['gitDir']
                    prefixCmdParent = 'cd %s' % os.path.dirname(gitPath)
                    prefixCmd = 'cd %s' % gitPath
                    
                    print '=' * 22
                    print '=== server=', node
                    print '=== git path=', gitPath
                    
                    runRemoteCmd(client, 'hostname', prefix=prefixCmd)
                    # set up PATH or some git commands fails
                    #runRemoteCmd(client, envCmds[node], prefix=prefixCmd)

                    runRemoteCmd(client, 'pwd', prefix=prefixCmd)
                    runRemoteCmd(client, 'sudo rm -fr %s' % gitPath, prefix=prefixCmdParent)
                    gitCloneCmd = 'git clone ssh://$USER@stash.wrs.com:7999/vx7/vxworks.git vxworks --branch %s --single-branch --depth 10' % branch
                    runRemoteCmd(client, gitCloneCmd, prefix=prefixCmdParent)
                    runRemoteCmd(client, 'git reset --hard %s' % commit, prefix=prefixCmd)
                    runRemoteCmd(client, './setup-tools -site pek', prefix=prefixCmd)
                    runRemoteCmd(client, 'git status', prefix=prefixCmd)
                    """
                    # remove the local existed branch in case that remote branch re-creates
                    if [ "$BRANCH" != "vx7-net" ]; then
                        # note: cat has to be added to the end of this pipe, or grep might generate -1 and all script gets exit here
                        BranchName=`git branch -r | grep -w $BRANCH | cat`
                        if [ "$BranchName" != "" ]; then
                            echo "found $BRANCH"
                            git branch -D $BRANCH
                        else
                            echo "not found $BRANCH"
                            exit 1
                        fi
                    fi
                    """               
                except Exception, e:
                    print('%s' % str(e))
                    returnCode = 1
                finally:
                    client.close()
                    if returnCode:
                        sys.exit(returnCode)
                    
            
def CopyWorkAroundFile(ssh, gitPath):
    dstPkgPath = gitPath + '/helix/guests/vxworks-7/pkgs_v2'
    srcPkgPath = '/net/pek-vx-nightly3/buildarea3/lchen3/vxworks/helix/guests/vxworks-7/pkgs_v2'

    changedFiles = ( '/net/ipnet/NOT_IMPORTED/iptestengine/config/config.py',
                     '/net/ipnet/coreip/src/ipcom/util/scripts/runKong.sh',
                     '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite.py',
                     '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_build.py',
                     '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_common.py',
                     '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_conf.py',
                     '/net/rtnet/test/socktest/rwtasks.c',
                   )

    print '\n=== copy branch work around files ==='
    for f in changedFiles:
        srcPath = srcPkgPath + f 
        dstPath = dstPkgPath + f    
        print 'copy from %s to %s' % (srcPath, dstPath)       
        ssh.SendCmd('cp %s %s' % (srcPath, dstPath))    

                
def main():
    if len(sys.argv) != 3:
        print 'usage: %s branch commit' % os.path.basename(sys.argv[0])
        sys.exit(1)
        
    branch = sys.argv[1]
    newCommit = sys.argv[2]
    
    if branch.startswith('SPIN:'):
        print 'handle %s' % branch
        spinPath = '/net/%s/%s' % (GetImageServer(), branch.replace('SPIN:', ''))
        if not os.path.exists(spinPath):
            print '%s not found' % spinPath
            sys.exit(1)
    else:
        HandleBranch(branch, newCommit)
        for node in kongBuildServers:
            gitPath=kongBuildServers[node]['gitDir']
        CopyWorkAroundFile4Git(gitPath, gitPath, 'git')
        CopyKongTestCasePatch4Git(gitPath, gitPath, 'git')

    KongBuild.BuildAllImage(branch, newCommit)

if __name__ == '__main__':
    main()
    
