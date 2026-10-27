#!/usr/bin/env python
import os
import sys

sys.path.insert(0, '/home/xli3/pytestAuto/utils')
from InstallSpin import InstallSpin, InstallLicense
import KongConfig, nightlyInfo
import shutil


def install_spin():
    # get spin information
    nightly_date, release_name, spin, branch = nightlyInfo.nightlyInfo()
    print("spin is %s" % spin)
    print("branch is %s" % branch)
    if spin == "":
        print("==== no spin=====")
        sys.exit(1)
    else:
        print('=== start to install spin:%s' % spin)
    # remove old spin start
    spinDir = "/home/xli3/SPIN"
    os.chdir(spinDir)
    os.system("rm -rf *")
    # install spin
    ret, result = InstallSpin(KongConfig.spinConfig[branch]['fromBaseDir'],
                              KongConfig.spinConfig[branch]['spinToDir'],
                              spin,
                              KongConfig.spinConfig[branch]['profile'])
    if ret != 0:
        print('=== fail  to install spin:%s' % spin)
        print('=== result:', result)
        sys.exit(1)
    print('=== done  to install spin:%s' % spin)
    print('=== start to install license')
    ret, result = InstallLicense(KongConfig.spinConfig[branch]['spinToDir'], spin)
    if ret != 0:
        print('=== fail  to install license')
        print('=== result:', result)
        sys.exit(1)
    print('=== done  to install license')

    # vxtest
    tmpDir = spinDir + '/' + spin
    tmp = tmpDir + '/vxworks/'
    vxver = os.listdir(tmp)[0]
    print('vxver is', vxver)
    #src = '/home/wrsadmin/iperf3'
    #dst = tmpDir + '/vxworks/' + vxver + '/source/contrib/iperf3'
    #shutil.copytree(src, dst)  # dst must not exist
    tmp = tmpDir + '/vxworks/' + vxver
    os.chdir(tmp)
    os.system(r'tar xf vxTest.tar')
    return tmpDir


if __name__ == '__main__':
    install_spin()
