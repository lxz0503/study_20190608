import os
import re
import sys
import shutil

from os.path import basename, dirname, join, exists
from commands import getoutput
from Action import ExecCmd
from Git import *

def InstallKongPatch(spinPath, gitPath, branch, version=7):
    print('=== spinPath=%s, gitPath=%s, branch=%s' % (spinPath, gitPath, branch))
    git = VxWorksGit(gitPath)
    git.UpdateBranch(branch) # run git.Setuptool() # for CopySysViewer

    CopyKongTestCase(gitPath, spinPath, version)
    CopyKongTestEngine(gitPath, spinPath, version)
    CopyKongScript(gitPath, spinPath, version)
    CopySysViewer(gitPath, spinPath)
    if spinPath.find('/HELIXSPIN/') != -1 or spinPath.find('/HELIXCISPIN/') != -1:
        CopyVxsim(gitPath, spinPath)
    CopyWorkAroundFile(gitPath, spinPath, version)
    CopyKongTestCasePatch(gitPath, spinPath, version)
    print('=== InstallKongPath finished. ===')

def GenerateSpinPath(spinBasePath, gitRelativePath):
    tokens = filter(lambda x: x not in ('.', '/'), gitRelativePath.split('/'))
    retTokens = list(tokens)
    
    currentPath = spinBasePath
    for i in xrange(len(retTokens)):
        tryPath = currentPath + '/' + retTokens[i]
        version = GetVersionPath(tryPath)
        if version != tokens[i]:
            retTokens[i] = version
        currentPath += '/' + retTokens[i]
        
    return '/'.join(retTokens)
    

def FindSpinPath(spinBasePath, gitRelativePath, directory=True):
    fs = os.listdir(spinBasePath)
    for f in fs:
        if f.startswith(gitRelativePath):
            if directory and os.path.isdir(os.path.join(spinBasePath, f)):
                return os.path.join(spinBasePath, f)
            elif not directory and not os.path.isdir(os.path.join(spinBasePath, f)):
                return os.path.join(spinBasePath, f)
    return ''

     
def GetVersionPath(tryPath):
    # return the basename with version according to installed spin directories
    if exists(tryPath):
        return basename(tryPath)
    else:
        if exists(dirname(tryPath)):
            dirs = os.listdir(dirname(tryPath))
            for d in dirs:
                if d.startswith(basename(tryPath + '-')):
                    return d
            return basename(tryPath)
        else:
            return basename(tryPath)
                    

def RemoveVersion(theStr):
    # 'ipnet-1.1.1.2/linkproto/l2tp-1.0.0.7/test'
    tokens = map(lambda x: x.split('-')[0], 
                 filter(lambda x: x not in('.', '/'), theStr.split('/'))
                )
    if theStr[0] == '/':
        return '/' + '/'.join(tokens)
    else:
        return '/'.join(tokens)
        
    
def test_GenerateSpinPath():
    basePath = spinPath + '/vxworks-7/pkgs/net'
    os.chdir(basePath)
    spinPaths = filter(lambda x: x.strip(), getoutput('find . -type d').split('\n'))

    # test case 1
    for sp in spinPaths[1:]:
        expected = sp.replace('./', '')
        sp1 = RemoveVersion(expected)
        versioned = GenerateSpinPath(basePath, sp1)

        if expected == versioned:
            print 'PASS : expected:%s, actual:%s' % (expected, versioned)
        else:
            print 'FAIL : expected:%s, actual:%s' % (expected, versioned)

    # test case 2
    testPaths = ('/testcloud/svc-cmnet/vxworks/vxworks-7/pkgs/net/ipnet/coreip/src/ipnet2',
            '/testcloud/svc-cmnet/vxworks/vxworks-7/pkgs/net/ipnet/ssh',
            '/testcloud/svc-cmnet/vxworks/vxworks-7/pkgs/net/ipnet/NOT_IMPORTED/ipcrypto',
            '/testcloud/svc-cmnet/vxworks/vxworks-7/pkgs/net/ipnet/NOT_IMPORTED/iptestengine',
           )

    for tp in testPaths:
        _, gitRelativePath = tp.split('/net/')
        versioned = GenerateSpinPath(basePath, gitRelativePath)
        print versioned


def CopyKongTestCase(gitPath, spinPath, version=7):
    print '\n=== copy Kong test cases ==='
    testCasePaths = [('/net', '/net'), 
                     ('/security', '/security'), 
                     ('/app', '/app'),
                    ]
    srcPkgsPath, _ = get_vxworks_env(gitPath)
    dstPkgsPath, _ = get_vxworks_env(spinPath)
    
    for sp, dp in testCasePaths:
        netGitPath = srcPkgsPath + sp
        netSpinPath = dstPkgsPath + dp
        
        if os.path.exists(netGitPath) and os.path.exists(netSpinPath):
            os.chdir(netGitPath)
            cmd = 'find . -type d | grep -v NOT_IMPORTED | grep \"/test$\"'
            ret, result = ExecCmd(cmd)
            if ret != 0:
                print 'cmd failed: %s' % cmd
                sys.exit(1)
            
            for x in filter(lambda x: x.strip() != '', result.split('\n')):
                srcPath = netGitPath + '/' + x
                dstPath = netSpinPath + '/' + GenerateSpinPath(netSpinPath, x)
                __CopyTree(srcPath, dstPath)

def CopyKongTestEngine(gitPath, spinPath, version=7):
    print '\n=== copy Kong test engine ==='
    srcPkgsPath, _ = get_vxworks_env(gitPath)
    dstPkgsPath, _ = get_vxworks_env(spinPath)
        
    netGitPath = srcPkgsPath + '/net'
    netSpinPath = dstPkgsPath + '/net'
        
    srcPath = netGitPath + '/ipnet/NOT_IMPORTED'
    dstPath = netSpinPath + '/' + GenerateSpinPath(netSpinPath, 'ipnet/NOT_IMPORTED')
    __CopyTree(srcPath, dstPath)

    
def CopyKongScript(gitPath, spinPath, version=7):
    print '\n=== copy Kong test scripts ==='
    srcPkgsPath, _ = get_vxworks_env(gitPath)
    dstPkgsPath, _ = get_vxworks_env(spinPath)
        
    netGitPath = srcPkgsPath + '/net'
    netSpinPath = dstPkgsPath + '/net'
    
    srcPath = netGitPath + '/ipnet/coreip/src/ipcom/util/scripts'
    dstPath = netSpinPath + '/' + GenerateSpinPath(netSpinPath, 'ipnet/coreip/src/ipcom/util/scripts')    
    __CopyTree(srcPath, dstPath)


def CopySysViewer(gitPath, spinPath):
    print '\n=== copy sys viewer ==='
    sysviewerGitPath = gitPath + '/workbench-4/wrsysviewer'
    sysviewerSpinPath = spinPath + '/workbench-4/wrsysviewer'
    __CopyTree(sysviewerGitPath, sysviewerSpinPath)


def CopyVxsim(gitPath, spinPath):
    print '\n=== copy vxsim ==='
    srcPkgsPath = '/net/pek-vx-nwk1/buildarea1/svc-cmnet/patch'
    dstPkgsPath, _ = get_vxworks_env(spinPath)
    changedDirs = ( 
                     '/os/arch/simulator-2.0.3.1',
                     '/os/arch/ia_share',
                     '/os/board/wrs/vxsim-2.0.0.6',
                   )
    for f in changedDirs:
        srcPath = srcPkgsPath + '/' + os.path.basename(f) 
        dstPath = dstPkgsPath + '/' + f  
        __CopyTree(srcPath, dstPath)

    srcPkgsPath = '/net/pek-vx-nwk1/buildarea1/svc-cmnet/patch/build-tool'
    changedFiles = ( 
                     '/common/krnl/defs.sim.mk',            # ./common/krnl/defs.sim.mk
                     '/common/usr/defs.simlinux.mk',        # ./common/usr/defs.simlinux.mk
                     '/llvm/krnl/defs.SIMLINUX.mk',        # ./llvm_2016_04/krnl/defs.SIMLINUX.mk
                     '/llvm/usr/defs.SIMLINUX.mk',         # ./llvm_2016_04/usr/defs.SIMLINUX.mk
                   )
    for f in changedFiles:
        srcPath = srcPkgsPath + '/' + f 
        if f.find('/llvm/') != -1:
            llvmPath = FindSpinPath(dstPkgsPath + '/../build/tool/', 'llvm')
            dstPath = llvmPath + f.replace('/llvm', '')
        else:
            dstPath = dstPkgsPath + '/../build/tool/' + f
        print('copy from %s to %s\n' % (srcPath, dstPath))  
        shutil.copyfile(srcPath, dstPath)

        
def __CopyTree(srcPath, dstPath): 
    print 'copy from %s to %s\n' % (srcPath, dstPath)       
    if exists(dstPath):
        shutil.rmtree(dstPath)
    shutil.copytree(srcPath, dstPath)


def CopyWorkAroundFile(gitPath, spinPath, version=7):
    if spinPath.find('653SPIN') != -1:
        # if it's 653SPIN
        print '\n=== copy spin work around files ==='
        dstPkgsPath, _ = get_vxworks_env(spinPath)
        gitPkgsPath, _ = get_vxworks_env(gitPath)
    
        # srcPkgsPath should be at vx7-integration branch, which has latest runtestsuite*.py
        srcPkgsPath = '/net/pek-cc-pb02l/testcloud/svc-cmnet/vxworks-nightly/helix/guests/vxworks-7/pkgs_v2'
        
        changedFiles = ( '/net/ipnet/NOT_IMPORTED/iptestengine/config/config.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runKong.sh',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_build.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_common.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_conf.py',
                         '/net/rtnet/test/socktest/rwtasks.c',
                       )
                
        # 653 spin is using old config files but latest scripts since it comes from SR0540
        gitFilesFor653 = ('/net/ipnet/NOT_IMPORTED/iptestengine/config/config.py',
                          '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_conf.py',
                         )
    
        confFileFor653 = ('/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_conf.py',
                         )    
        
        for f in changedFiles:
            if spinPath.find('653SPIN') != -1 and f in gitFilesFor653:
                srcPath = gitPkgsPath + f 
                dstPath = dstPkgsPath + GenerateSpinPath(dstPkgsPath, f)  
                print 'copy from %s to %s\n' % (srcPath, dstPath)       
                shutil.copyfile(srcPath, dstPath)
                if f in confFileFor653:
                    Handle653ConfFile(dstPath)
                continue
            srcPath = srcPkgsPath + f 
            dstPath = dstPkgsPath + GenerateSpinPath(dstPkgsPath, f)  
            print 'copy from %s to %s' % (srcPath, dstPath)       
            shutil.copyfile(srcPath, dstPath)  
    else:
        # temporary solution for ping with default number
        if version != 'git':
            print '\n=== copy spin work around files for Helix spin ==='
        else: 
            print '\n=== copy Kong script work around files for git ==='

        srcPkgsPath = '/net/pek-vx-nwk1/buildarea1/svc-cmnet/patch/script'
        dstPkgsPath, _ = get_vxworks_env(spinPath)

        changedFiles = ( 
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runKong.sh',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_conf.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_common.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuite_build.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/target.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/util.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/qemuTargetConfig.yaml',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/vxBuild.py',
                         '/net/ipnet/coreip/src/ipcom/util/scripts/vxBuildConfig.yaml',
                       )

        for f in changedFiles:
            srcPath = srcPkgsPath + '/' + os.path.basename(f) 
            dstPath = dstPkgsPath + GenerateSpinPath(dstPkgsPath, f)  
            if os.path.isfile(srcPath):      
                print 'copy from %s to %s' % (srcPath, dstPath)
                shutil.copyfile(srcPath, dstPath)
            elif os.path.isdir(srcPath):
                __CopyTree(srcPath, dstPath)
              
def CopyKongTestCasePatch(gitPath, spinPath, version=7):
    print '\n=== copy Kong test cases patches ==='

    testCasePaths = [('/net/rtnet/test/rtnet/test/', ['command.py','command_rtp.py','socktest.py'], '/net', 'rtnet/test/rtnet/test'),
                     ('/net/ipnet/linkproto/rohc/test/tcp/test/', ['iprohc_tcp.py'], '/net', 'ipnet/linkproto/rohc/test/tcp/test'),
                     ('/net/ipnet/linkproto/rohc/test/udp/test/', ['iprohc_udp.py'], '/net', 'ipnet/linkproto/rohc/test/udp/test'),
                     ('/net/ipnet/coreip/src/ipnet2/test/', ['ip4.py'], '/net', 'ipnet/coreip/src/ipnet2/test'),
                     ('/net/ipnet/coreip/src/ipnet2/test/socktest/test/', ['taccept6.c','test6.h','tmain6.c','xaccept6.c'], '/net', 'ipnet/coreip/src/ipnet2/test/socktest/test'),
                     ('/net/rtnet/test/sock6test/', ['taccept6.c','test6.h','tmain6.c','xaccept6.c'], '/net', 'rtnet/test/sock6test'),
                     ('/net/ipnet/qos/test/', ['qos.py','diffserv.py'], '/net', 'ipnet/qos/test'),
                     ('/net/ipnet/ssh/test/', ['ipssh_test.py'], '/net', 'ipnet/ssh/test'),]
    
    srcPkgsPath = '/net/pek-vx-nwk1/buildarea1/svc-cmnet/patch'
    dstPkgsPath, _ = get_vxworks_env(spinPath)

    for sp, testFiles, dp, rp in testCasePaths:
        casePatchPath = srcPkgsPath + sp
        caseSpinPath = dstPkgsPath + dp

        dstPath = caseSpinPath + '/' + GenerateSpinPath(caseSpinPath, rp)
        for testfile in testFiles:
            srcFile = casePatchPath + testfile
            dstFile = dstPath + '/' + testfile
            shutil.copyfile(srcFile, dstFile)
            print('copy from %s to %s' % (srcFile, dstFile))
    print '\n=== copy Kong test cases finished ==='

def Handle653ConfFile(runtestsuite_confFile):
    print '\n=== handling 653 %s ===' % runtestsuite_confFile
    with open(runtestsuite_confFile, 'r') as fd:
        content = fd.read()
        found = re.search('(?s)(testable_packages_search_paths\s+=\s+\[.*?\])', content)
        if found is not None:
            oldStr = found.groups()[0]
        else:
            raise BaseException('testable_packages_search_paths not found in %s' % runtestsuite_confFile)
        newStr = oldStr.replace('/vxworks-7/pkgs', '')
    
    with open(runtestsuite_confFile, 'w') as fd:
        newContent = content.replace(oldStr, newStr)
        newContent = newContent.replace('\'/pkgs/', '\'/')  # USERDB, USERAUTH_LDAP
        fd.write(newContent)
    

def get_vxworks_env(install_path):
    base4relx = install_path + '/vxworks'
    if os.path.exists(base4relx):
        envdir = os.listdir(base4relx)
        envstr = 'vxworks/' + envdir[0]
        wrenv_prefix = '%s/wrenv.sh -p %s' % (install_path, envstr) 
        # get pkgs_path from $WIND_PKGS
        cmd = wrenv_prefix + ' env | grep WIND_PKGS='
        ret, result = ExecCmd(cmd)
        pkgs_path = result.strip().lstrip('WIND_PKGS=')
    elif os.path.exists(install_path + '/helix/guests/vxworks-7'):
        pkgs_path = install_path + '/helix/guests/vxworks-7/pkgs_v2'
        wrenv_prefix = '%s/wrenv.sh -p helix' % install_path
    elif os.path.exists(install_path + '/vxworks-7'):
        if os.path.exists(install_path + '/vxworks-7/pkgs_v2'):
            pkgs_path = install_path + '/vxworks-7/pkgs_v2'
            wrenv_prefix = '%s/wrenv.sh -p vxworks-7' % install_path
        elif os.path.exists(install_path + '/vxworks-7/pkgs'):
            pkgs_path = install_path + '/vxworks-7/pkgs'
            wrenv_prefix = '%s/wrenv.sh -p vxworks-7' % install_path
        else:
            raise BaseException('%s vxworks-7 has neither pkgs_v2 nor pkgs' % install_path)
    elif os.path.exists(install_path + '/vxworks-653'):
        pkgs_path = install_path + '/vxworks-653/pkgs'
        wrenv_prefix = '%s/wrenv.sh -p vxworks-653' % install_path
    else:
        raise BaseException('%s not correct since vxworks-7, vxworks-653 and helix/guests/vxworks-7 was not found' % install_path)
    return pkgs_path, wrenv_prefix

    
def main():
    branch = 'vx7-integration'
    gitPath  = '/buildarea1/svc-cmnet/vxworks-latest'
    spinPath = '/buildarea1/svc-cmnet/HELIXSPIN/vx20190815060702_vx7-helix'

    InstallKongPatch(spinPath, gitPath, branch)
    
if __name__ == '__main__':
    main()
    #test_GenerateSpinPath()
    
    
