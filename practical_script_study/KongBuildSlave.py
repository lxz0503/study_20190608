#!/usr/bin/env python

# Jenkins build slave job
#    build vxworks images among kongBuildServers

# need to add the following line to the server /etc/ssh/sshd_config
#     KexAlgorithms diffie-hellman-group-exchange-sha1
# and then restart ssh by the command below to avoid the error "Incompatible ssh peer (no acceptable kex algorithm)"
#     sudo service ssh restart

import argparse
import os
import shutil
import socket
import sys

from runtestsuite_common import get_vxworks_env

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import paramiko
from paramiko import SSHClient

local_kongBuildServers = {
                    'pek-sec-kong-02' : { 'node' : 'pek-sec-kong-02',
                                          'gitDir' : '/workspace/svc-cmnet/vxworks', 
                                        },
                    'pek-cc-pb02l'    : {
                                          'node' : 'pek-vx-nwk1', # use remote build node
                                          'gitDir' : '/buildarea1/svc-cmnet/vxworks',
                                        },
                   }

def isLocalBuild(hostName):
    host = hostName.split('.')[0]
    buildNode = local_kongBuildServers[host]['node']
    if host == buildNode:
        return True
    else:
        return False    
    
def local_GetBuildNode(hostName):
    host = hostName.split('.')[0]
    return local_kongBuildServers[host]['node']
    
local_kongImageDir = 'pek-sec-kong-02:/workspace/svc-cmnet/IMAGES'

def local_GetImageServer():
    return local_kongImageDir.split(':')[0]

def local_GetImageDir():
    return local_kongImageDir.split(':')[1]

supportedBsps = ('vxsim_linux', 'fsl_imx6', 'itl_generic', )

passValue = 0
failValue = 10

debugFlag = False # boolean to turn on/off debug log
shcmdIndicator = '===='

def shCmd(cmd, sudo=False):
    if sudo:
        cmd = 'sudo ' + cmd
    if debugFlag:
        print('%s %s' % (shcmdIndicator, cmd))
    return os.popen(cmd).readlines()


def runLocalBuild(module, cmd, buildPath):
    print('run local build')
    
        
def runRemoteBuild(node, module, cmd, buildPath):
    def checkRemoteFile(client, theFile):
        try:
            cmd = '[ -f %s ] && echo 1 || echo 0' % theFile
            _, stdOut, stdErr = client.exec_command('%s' % cmd)
            output = stdOut.read()
        except Exception, e:
            print('%s' % str(e))
        finally:    
            if output.strip() == '1':
                print('found')
                return True
            else:
                print('not found')
                return False
            
    username = 'svc-cmnet'
    password = 'december2012!'
    scriptFiles = ('runtestsuite.py',
                   'runtestsuite_conf.py',
                   'runtestsuite_common.py',
                   'runtestsuite_build.py',
                   'vlmTarget.py',
                   'shellUtils.py',
                   'lockboard.py',
                   )
    try:
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(node, username=username, password=password)
        print('\nbuild at remote node:%s' % node)
        #for script in scriptFiles:
        #    _, stdOut, _ = client.exec_command('cd %s && cp %s/%s .' % (buildPath, os.path.dirname(cmd), script))
        #    print(stdOut.read())
        _, stdOut, stdErr = client.exec_command('cd %s && sudo rm -fr %s' % (buildPath, module))
        print(stdOut.read())
        print('build cmd: cd %s && %s' % (buildPath, cmd))
        _, stdOut, stdErr = client.exec_command('cd %s && %s' % (buildPath, cmd))
        output = stdOut.read()
        print('build out:%s' % output) #.decode('utf-8').split('\n')
        #print('build err:%s' % stdErr.read()) #.decode('utf-8').split('\n')
    finally:    
        imagePath = '%s/%s/vxsim_linux_vip/default' % (buildPath, module)
        if checkRemoteFile(client, imagePath + '/vxWorks') or \
           checkRemoteFile(client, imagePath + '/uVxWorks'):
            #print 'return %s' % passValue
            return passValue
        else:
            #print 'return %s' % failValue
            return failValue        


def parseArgument(argv):
    parser = argparse.ArgumentParser(description='Build vxworks image')
    parser.add_argument('--branch', action='store', dest='branch', help='specify the git branch to build (required)')
    parser.add_argument('--commit', action='store', dest='commit', help='specify the commit to build (required)')
    parser.add_argument('--module', action='store', dest='module', help='specify the module to build (required)')
    parser.add_argument('--bsp', action='store', dest='bsp', help='specify the bsp to build (required)')
    parser.add_argument('--64bit', action='store_true', dest='m64bit', help='specify the 64bit to build (optional)')
    args = parser.parse_args()

    if (args.branch is None) or (args.commit is None) or (args.module is None) or (args.bsp is None):
        parser.print_help()
        exit(1)

    return args


def getGitPath(branch):
    return branch.replace('SPIN:', '')


def checkBsp(bsp):
    if bsp in supportedBsps:
        return bsp
    else:
        raise Exception('%s is not supported bsp. only %s supported' % (bsp, supportedBsps))
    

def checkPath(thePath):
    if not os.path.exists(thePath):
        raise Exception('%s not found' % thePath)


def createModuleTarFile(tarFile, module, modulePath, scriptPath):
    """ SNTP_SERVER and SSH is special """
    def getVipPath(modPath):
        dirs = [x for x in os.listdir(modPath) if os.path.isdir('%s/%s' % (modPath, x))]
        for bsp in supportedBsps:
            vip = '%s_vip' % bsp
            if vip in dirs:
                return vip
        raise Exception('not found valid VIP path in %s' % modulePath)
    
    def prepareTarArgument(modulePath, scriptPath): 
        checkPath(modulePath)
        checkPath(scriptPath)
        # copy necessary python scripts for tar file
        scripts = ('runtestsuite.py',
                   'runtestsuite_common.py',
                   'runtestsuite_conf.py',
                   'runtestsuite_build.py',
                   'vlmTarget.py',
                   'shellUtils.py',
                   'lockboard.py',
                   'runKong.sh',
                  )
        for script in scripts:
            scriptFile = '%s/%s' % (scriptPath, script)
            checkPath(scriptFile)
            shutil.copy(scriptFile, modulePath)
    
        # create tar command using relative path
        tarArgument = ''
        vip = getVipPath(modulePath)
        tarList = ['/cvs', 
                   '/%s/default/vxWorks*' % vip, 
                   '/%s/default/uVxWorks' % vip,
                   '/%s/default/*.dtb' % vip,
                  ] + list(scripts)
        for f in tarList:
            if f.find('*') == -1:
                if os.path.exists('%s/%s' % (modulePath, f)):
                    tarArgument += ' %s/%s' % (os.path.basename(modulePath), f)
            else:
                tarArgument += ' %s/%s' % (os.path.basename(modulePath), f)
        return tarArgument

    # run tar command    
    oldCwd = os.getcwd()
    tarFilePath = '%s/%s' % (oldCwd, tarFile)
    os.system('rm -f %s' % tarFilePath)
    os.chdir(os.path.dirname(modulePath))
    
    tarCmd = 'tar zcf ' + tarFilePath + prepareTarArgument(modulePath, scriptPath)
    if module == 'SNTP_SERVER':
        tarCmd += prepareTarArgument('%s/%s' % (os.path.dirname(modulePath), 'SNTP_CLIENT'), scriptPath)
    print(tarCmd)
    os.system(tarCmd)
    os.system('chmod 755 %s' % tarFilePath)
    os.chdir(oldCwd)
    return tarFilePath
        

def testRemoteCheckFile():
    username = 'svc-cmnet'
    password = 'december2012!'
    testPassFlag='Info: tinderbox: status: success'
    node = 'pek-vx-nwk1.wrs.com'
    #node = '128.224.153.34'
    output = ''
    try:
        client = SSHClient()
        print('==1==')
        client.load_system_host_keys()
        print('==2==')
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print('==3==')
        client.connect(node, username=username, password=password)
        print('==4==')
        _, stdOut, stdErr = client.exec_command('hostname && pwd')
        print('==5==')
        output = stdOut.read()
        print('==6==')
        print('build out:%s' % output) #.decode('utf-8').split('\n')
        print('build err:%s' % stdErr.read()) #.decode('utf-8').split('\n')
                
        cmd = '[ -f /buildarea1/svc-cmnet/vxworks/wrenv.linux ] && echo 1 || echo 0'
        _, stdOut, stdErr = client.exec_command('%s' % cmd)
        output = stdOut.read()
        print('build out:%s' % output) #.decode('utf-8').split('\n')
        print('build err:%s' % stdErr.read()) #.decode('utf-8').split('\n')
    except Exception, e:
        print('%s' % str(e))
    finally:    
        if output.strip() == '1':
            print('found')
            return 1
        else:
            print('not found')
            return 0
        client.close()


def main():
    args = parseArgument(sys.argv)
    hostName = socket.gethostname()

    bsp = 'vxsim_linux' if args.bsp is None else checkBsp(args.bsp)
    flag64bit = '-lp64' if args.m64bit else ''
    
    if isLocalBuild(hostName):
        git = getGitPath(args.branch)
        pkgs_path, _ = get_vxworks_env(git)
        runKongScriptPath = pkgs_path + '/net/ipnet*/coreip*/src/ipcom/util/scripts'
                
        buildPath = '/workspace/svc-cmnet/temp'
        buildCmd = '%s/runKong.sh %s -g %s -m %s -b %s buildOnly' % (runKongScriptPath, flag64bit, git, args.module, bsp)
        buildRet = runLocalBuild(args.module, buildCmd, runKongScriptPath)
    else:
        git = getGitPath('/net/%s/%s' % (local_GetImageServer(), args.branch))
        pkgs_path, _ = get_vxworks_env(git)
        runKongScriptPath = pkgs_path + '/net/ipnet*/coreip*/src/ipcom/util/scripts'        
        
        node = local_GetBuildNode(hostName)
        buildPath = '/buildarea1/svc-cmnet/temp'
        buildCmd = '%s/runKong.sh %s -g %s -m %s -b %s buildOnly' % (runKongScriptPath, flag64bit, git, args.module, bsp)
        buildRet = runRemoteBuild(node, args.module, buildCmd, buildPath)
    
    if buildRet == failValue:
        print('build failed')
        sys.exit(failValue)
    else:
        print('build passed')
        sys.exit(buildRet)
    
    
if __name__ == '__main__':
    main()
    #testRemoteCheckFile()
        
