#!/usr/bin/env python
# this script is just used after rerun and update LTAF

import os,sys,time,ConfigParser
import resultDir 
import nightlyInfo

def updateLtaf(dir):
    os.chdir(dir)
# write test result into LTAF start

    with open("test_result.log","r") as fd:
        for line in fd.readlines():
            test_name = line.split(":")[0]
            case_status = line.split(":")[1].strip("\n")
			
# print case_status,set initial status as 0
            status = "Fail"
            funtion_pass = 0
            function_fail = 0
            if  case_status == "Passed":
                status = "Pass"
                function_pass = 1
            elif case_status == "!FAILED!":
                status = "Fail"
                function_fail = 1
            else:
                print "Test case result is INCLUSIVE!Please check test log!"
				
# modify  nightly.ini file
            log = "http://pek-cc-pb08l.wrs.com/vxtest/vxtest1/LOG_VX7/Vx-7_Networking/REGRESSION/vxworks_sandbox/ANVL"
            nightly_date,release_name,spin = nightlyInfo.nightlyInfo()
            # print nightly_date,release_name,spin
			
            config = ConfigParser.ConfigParser()
            config.read("/home/windriver/ANVL/nightly.ini")
            config.set("LTAF","test_name",test_name)
            config.set("LTAF","status",status)
            config.set("LTAF","function_pass",function_pass)
            config.set("LTAF","function_fail",function_fail)
            config.set("LTAF","spin",spin)
            config.set("LTAF","log",log)
            config.set("LTAF","week",nightly_date)
            config.set("LTAF","release_name",release_name)
            config.write(open('/home/windriver/ANVL/nightly.ini',"r+"))
            os.system("curl -F resultfile=@/home/windriver/ANVL/nightly.ini http://pek-lpgtest3.wrs.com/ltaf/upload_nightly_results.php")
            os.system("cp /home/windriver/ANVL/LTAF/nightly.ini /home/windriver/ANVL")
			
def main():
    dir = resultDir.enterDir()
    updateLtaf(dir)

if __name__ == '__main__':
    main()
