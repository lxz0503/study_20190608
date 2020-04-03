#!/usr/bin/env python
import os,sys,time,string,ConfigParser
from InstallSpin import InstallSpin, InstallLicense, GetSpinInfo
import  KongConfig
import analyze,calculate,uploadLog,nightlyInfo,resultDir

def main():
    # check anvl server status
    cmd = "ping 128.224.166.46 -c 1"
    process = os.popen(cmd)
    output = process.read()
    process.close()
    if "icmp_req" in output:
        print "anvl server is ok"
    else:
        print "anvl server is not ok"
        sys.exit(1)
#get spin information
    branch = "SPIN"
    nightly_date,release_name,spin = nightlyInfo.nightlyInfo()
    if spin == "":
        print "==== no spin====="
        sys.exit(1)
    else:
        print '=== start to install spin:%s' % spin
#remove old spin start
    spinDir = "/home/windriver/SPIN"
    os.chdir(spinDir)
    os.system("rm -rf *")
#install spin
    ret, result = InstallSpin(KongConfig.spinConfig[branch]['fromBaseDir'],
                              KongConfig.spinConfig[branch]['spinToDir'],
                              spin,
                              KongConfig.spinConfig[branch]['profile'])
    if ret != 0:
        print '=== fail  to install spin:%s' % spin
        print '=== result:', result
        sys.exit(1)
    print '=== done  to install spin:%s' % spin
    print '=== start to install license'
    ret, result = InstallLicense(KongConfig.spinConfig[branch]['spinToDir'], spin)
    if ret != 0:
        print '=== fail  to install license'
        print '=== result:', result
        sys.exit(1)
    print '=== done  to install license'
    tmpDir = "/home/windriver/SPIN" + "/" + spin
    os.chdir(tmpDir)
    os.system("cp -rf * /home/windriver/SPIN/")
#build image
    scriptDir = "/home/windriver/ANVL"
    os.chdir(scriptDir)
    build_cmd = r'/home/windriver/ANVL/buildRTNet.sh'
    os.system(build_cmd)    
# check image 
    if os.path.isfile('/home/windriver/SPIN/vip_itl_generic/default/vxWorks'):
        print 'image is ok'
    else:
        print 'no image was built,check log'
        sys.exit(1)
#run anvl test
    runCmdSpin = r'/home/windriver/ANVL/Conf_xiaozhan_trial.py -r ANVL --dvd="dvdUser=windriver,dvdPwd=windriver,dvdAddr=128.224.159.79,dvdPrompt=windriver@PEK-QCAO1-D2:~,dvdPath=/home/windriver/SPIN"  --bsp=itl_generic --tool=llvm --vxworks=7 --localFTP="ftpuser=windriver,ftppwd=windriver,ftpdir=/home/windriver/ANVL/ANVL_image" --localSSH="sshuser=windriver,sshpwd=windriver" --localAddr=128.224.159.79 --log=/home/windriver/ANVL/ANVL_Result --target="console=128.224.164.57 2016,pduAddr=128.224.164.113,pduPort=6,bootEth=gei,bootPort=2,bootIp=128.224.166.238:0xfffffe00"'
    os.system(runCmdSpin)
#analyze anvl test result and update LTAF
    dir = resultDir.enterDir()
    analyze.analyze(dir)
    calculate.calculate(dir)
    uploadLog.updateLtaf(dir)
if __name__ == '__main__':
    main()
