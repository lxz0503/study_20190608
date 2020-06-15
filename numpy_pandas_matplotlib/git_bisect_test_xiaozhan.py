#!/usr/bin/env python
import os,sys,time,string,ConfigParser,re
from InstallSpin import InstallSpin, InstallLicense, GetSpinInfo
import  KongConfig
import analyze,calculate,uploadLog,nightlyInfo,resultDir
from get_git_commit import set_git_commit,set_git_sign

debug = "exception"

def main():
#analyze anvl test result and update LTAF
        dir = resultDir.enterDir()
        print dir
        os.chdir(dir)
#just for ike exception
        if debug == "exception":
            cmd = """grep -rI "exception" ./"""
            r = os.popen(cmd).read()
            m = re.search("exception",r)
            try:
                if m is not None:
                    print m
                    #print m.group()
                # if m.group() == "exception":
                    result = "fail"
                else:
                    result = "pass"
            except Exception,e:
                print e
                
#exception end
        else:
            analyze.analyze(dir)
            r = calculate.calculate(dir)
            print "the pass rate is %s%%" % r
            if r == "100.0":
                result = "pass"
            else:
                result = "fail"
        print result
#write a function to get the result: pass or fail, return to the start of the loop
        #r = set_git_sign(spin_dir,result)
        #if r is not None:
            #print 'already find the first bad commit %s' % r
            #break


if __name__ == '__main__':
    main()
