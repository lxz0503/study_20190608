import os
import re
import sys
import time
import KongConfig

from Action import ExecCmd

# interface for vx7_nightly_spin.config, vx7_ci_nightly_spin.config and vx7_vx653_nightly_spin.config
# at /net/pek-vx-nightly1/buildarea1/pzhang1/jenkinsEnvInjection

def GetSpinInfo(commit, action):
    assert commit in KongConfig.spinConfig.keys()
    if commit == 'SPIN':
        configFile = 'vx7_nightly_spin.config'
    elif commit == 'CISPIN':
        configFile = 'vx7_ci_nightly_spin.config'
    elif commit == '653SPIN':
        configFile = 'vx7_vx653_nightly_spin.config'
    elif commit == 'LLVMSPIN':
        configFile = 'vx7_llvm_nightly_spin.config'        
    else:
        raise BaseException('branch %s is not valid' % commit)
    
    if action == 'name':
        return __GetNameValue('NIGHTLYSPIN', configFile)
    elif action == 'release':
        return __GetNameValue('LTAFRELEASE', configFile)
    elif action == 'date':
        tsStr = __GetNameValue('timestamp', configFile)
        if tsStr:
            return time.strftime('%Y-%m-%d', time.strptime(tsStr, '%Y%m%d%H%M%S'))
        else:
            return ''
    else:
        raise BaseException('action %s is not valid' % action)        
    
    
def __GetNameValue(name, configFile):
    debug = False
    if debug:
        configDir = '/net/pek-sec-kong-02/workspace/svc-cmnet/log'
    else:
        configDir = '/net/pek-vx-nightly1/buildarea1/pzhang1/jenkinsEnvInjection'

    spinConfig = configDir + '/' + configFile
    if not os.path.exists(spinConfig):
        raise BaseException('config file %s not found' % configFile)
            
    with open(spinConfig, 'r') as fd:
        content = fd.read()
        found = re.search('%s=(.*?)\n' % name, content)
        if found is not None:
            return found.groups()[0].strip()
        else:
            return ''

def InstallSpin(fromBaseDir, toDir, spin, profile):
    # return: retCode, retResult
    fromDir = fromBaseDir + '/' + spin
    if not os.path.exists(fromDir):
        print '%s not found' % fromDir
        return -1, ''
    if not os.path.exists(toDir):
        print '%s not found' % toDir
        return -1, ''
    
    cmd = 'cd %s; sudo rm -fr *' % toDir
    _, _ = ExecCmd(cmd)
    
    # use all profiles for installation
    cmd = 'cd {fromDir}/bootstrap_installer; ./setup_linux -installerUpdateURLs none -productUpdateURLs none -silent -installPath {toDir}  -yum -y install'.format(fromDir=fromDir, profile=profile, toDir=toDir + '/' + spin)
    print cmd
    retCode, retResult = ExecCmd(cmd)
    return retCode, retResult
     

def InstallLicense(spinToDir, spin):
    # return: retCode, retResult
    fromFile = '/net/pek-cdftp/pek-cdftp1/ftp/r1/license/WRSLicense.lic'
    if not os.path.exists(fromFile):
        print '%s not found' % fromFile
        return -1, '%s not existed' % fromFile
    toDir = spinToDir + '/' + spin + '/license'
    if not os.path.exists(toDir):
        print '%s not found' % toDir
        return -1, '%s not existed' % toDir
    
    cmd = 'cp %s %s/%s' % (fromFile, toDir, os.path.basename(fromFile))
    retCode, retResult = ExecCmd(cmd)
    return retCode, retResult
    
    
def test():
    print '|SPIN=%s|' % GetSpinInfo('SPIN', 'name')
    
    print '|SPIN RELEASE=%s|' % GetSpinInfo('SPIN', 'release')
    
    print '|timestamp=%s|' % GetSpinInfo('SPIN', 'date')
    
    print '|ci-branch timestamp=%s|' % GetSpinInfo('CISPIN', 'date')
    
    
        
def main():
    spinType = 'CISPIN'
    fromBaseDir = KongConfig.spinConfig[spinType]['fromBaseDir']
    profile = KongConfig.spinConfig[spinType]['profile']
    spinToDir = KongConfig.spinConfig[spinType]['spinToDir']

    spin = GetSpinInfo(spinType, 'name')
    spinRelease = GetSpinInfo(spinType, 'release')
    if spin and spinRelease:
        print spinToDir, spin, profile, spinRelease
        ret, _ = InstallSpin(fromBaseDir, spinToDir, spin, profile)
        if ret == 0:
            print '=== install ok'
        else:
            print '=== install fail'

        ret, _ = InstallLicense(spinToDir, spin)
        if ret == 0:
            print '=== install license file ok'
        else:
            print '=== install license file fail'
    else:
        print '=== no spin to install'


if __name__ == '__main__':
    main()
    #test()
        
