import os
import shutil

from HelixConfig import *

def getGitDir(host):
    return helixBuildServers[host]['gitDir']

def getAllGitDirs():
    rets = []
    for host in helixBuildServers:
        rets.append('/net/' + host + getGitDir(host))
    return ' '.join(rets)

def getServerName(nfsGitPath):
    # assume that git path is like /net/server_name/git_path
    return nfsGitPath.split('/')[2]

def getGitPath1(nfsGitPath):
    # assume that git path is like /net/server_name/git_path
    serverName = getServerName(nfsGitPath)
    return nfsGitPath.replace('/net/%s' % serverName, '')


def getImagePath():
    return helixImageDir

  
def getImageServer():
    return helixImageDir.split('/')[2]


def getImageLocalPath():
    server = getImageServer()
    return helixImageDir[len('/net/%s' % server):]


def getImageModulePath(module, bsp):
    return '%s/%s/%s' % (getImagePath(), bsp, module)
    
def getGitPath(branch):
    if branch.startswith('SPIN:'):
        return branch[len('SPIN:'):]
    else:
        return branch


def getScriptPath(gitPath):
    pkgsPath, _ = getVxWorksEnv(gitPath)
    return '%s/%s' % (pkgsPath, getSpinPath(pkgsPath, '/net/ipnet/coreip/src/ipcom/util/scripts'))


def getSpinPath(spinBasePath, gitRelativePath):
    tokens = filter(lambda x: x not in ('.', '/'), gitRelativePath.split('/'))
    retTokens = list(tokens)
    
    currentPath = spinBasePath
    for i in xrange(len(retTokens)):
        tryPath = currentPath + '/' + retTokens[i]
        version = getVersionPath(tryPath)
        if version != tokens[i]:
            retTokens[i] = version
        currentPath += '/' + retTokens[i]
        
    return '/'.join(retTokens)


def getVersionPath(tryPath):
    # return the basename with version according to installed spin directories
    if os.path.exists(tryPath):
        return os.path.basename(tryPath)
    else:
        if os.path.exists(os.path.dirname(tryPath)):
            dirs = os.listdir(os.path.dirname(tryPath))
            for d in dirs:
                if d.startswith(os.path.basename(tryPath + '-')):
                    return d
            return os.path.basename(tryPath)
        else:
            return os.path.basename(tryPath)


def getVxWorksEnv(install_path):
    if os.path.exists(install_path + '/helix/guests/vxworks-7'):
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


def checkPath(thePath):
    if not os.path.exists(thePath):
        raise Exception('%s not found' % thePath)
    

def createHelixTarFile(tarFile, modulePath):
    """ SNTP_SERVER and SSH is special """
    # run tar command    
    oldCwd = os.getcwd()
    tarFilePath = '%s/%s' % (oldCwd, tarFile)
    os.system('rm -f %s' % tarFilePath)
    
    os.chdir(os.path.dirname(modulePath))
    tarCmd = 'tar zcf %s %s/*' % (tarFilePath, os.path.basename(modulePath))
    print(tarCmd)
    os.system(tarCmd)

    os.system('chmod 755 %s' % tarFilePath)
    os.chdir(oldCwd)
    return tarFilePath


def getJenkinsUrl(job, buildId, jenkinsWeb='http://pek-testharness-s1.wrs.com:8080'):
    # http://pek-testharness-s1.wrs.com:8080/job/ci-build-slave/73771/console
    return '%s/job/%s/%s/console' % (jenkinsWeb, job, buildId)


def createTestArgument(module):
    MAX_ARG_STRLEN = 131072
    if module not in helixTestPlanToReport:
        return ''
    testNameWithIps = helixTestPlanToReport[module].keys()
    testNames = set([x.replace('- IPv4', '').replace('- IPv6', '').strip() for x in testNameWithIps])
    testNames = sorted(list(testNames))
    testArgument = ','.join(testNames)
    if len(testArgument) + 2000 >= MAX_ARG_STRLEN:
        raise Exception('created command line is too long')
    return testArgument


def test_createTestArgument():
    for mod in helixTestPlanToReport:
        testArg = createTestArgument(mod)
        print('%s : %s' % (mod, len(testArg)))


if __name__ == '__main__':
    test_createTestArgument()
    
