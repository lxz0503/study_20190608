#!/usr/bin/env python
import os,sys,time,string,ConfigParser,re
from InstallSpin import InstallSpin, InstallLicense, GetSpinInfo
import  KongConfig
import analyze,calculate,uploadLog,nightlyInfo,resultDir
from get_git_commit import set_git_commit,set_git_sign

def main():
#get spin information---write a function
    debug = "exception"  #  exception but case passed, False is just for case failed
    spin_dir = "/home/windriver/Integration/vxworks"
    good_commit = "b0bfef470626c7a7d640088a7fc05ebf98f32827"
    bad_commit = "7d95ca916aa06d481055df4800895e2dec649d9a"
    set_git_commit(spin_dir,good_commit,bad_commit)    # Ö´ÐÐgit bisect start, git bisect $badcommit, git bisect $goodcommit

#
    while True:
#build image
        os.chdir("/home/windriver/Integration/vxworks")
        os.system("rm -rf vsb*")
        os.system("rm -rf vip*")
        scriptDir = "/home/windriver/ANVL"
        os.chdir(scriptDir)
#how to move this to kong server ?????
        build_cmd = r'/home/windriver/ANVL/git_bisect_image.sh'
        os.system(build_cmd)    
# check image 
        if os.path.isfile('/home/windriver/Integration/vxworks/vip_itl_generic/default/vxWorks'):
            print 'image is ok'
        else:
            print 'no image was built,check log'
            sys.exit(1)
#run anvl test
        runCmdSpin = r'/home/windriver/ANVL/git_bisect_test.py -r ANVL --dvd="dvdUser=windriver,dvdPwd=windriver,dvdAddr=128.224.163.8,dvdPrompt=windriver@PEK-QCAO1-D2:~,dvdPath=/home/windriver/Integration/vxworks"  --bsp=itl_generic --tool=llvm --vxworks=7 --localFTP="ftpuser=windriver,ftppwd=windriver,ftpdir=/home/windriver/ANVL/ANVL_image" --localSSH="sshuser=windriver,sshpwd=windriver" --localAddr=128.224.163.8 --log=/home/windriver/ANVL/ANVL_Result --target="console=128.224.164.57 2016,pduAddr=128.224.164.113,pduPort=6,bootEth=gei,bootPort=2,bootIp=128.224.166.238:0xfffffe00"'
        os.system(runCmdSpin)
#analyze anvl test result and update LTAF
        dir = resultDir.enterDir()
        print dir
        os.chdir(dir)
#just for ike exception
        if debug == "exception":
            cmd = """grep -rI "exception" ./"""
            r = os.popen(cmd).read()
            m = re.search("exception",r)
            if m is not None:
                #print m.group()
                #if m.group() == "exception":
                result = "fail"
            else:
                result = "pass"
#exception end
        else:
            analyze.analyze(dir)
            r = calculate.calculate(dir)
            print "the pass rate is %s%%" % r
            if r == "100.0":
                result = "pass"
            else:
                result = "fail"

# write a function to get the result: pass or fail, return to the start of the loop
        r = set_git_sign(spin_dir,result)
        if r is not None:
            print 'already find the first bad commit %s' % r
            break


if __name__ == '__main__':
    main()
