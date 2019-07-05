#!/usr/bin/env python
import os,string
import resultDir


def calculate(dir):

    os.chdir(dir)
    cmd = """grep -rI ".*: Passed" ./ | awk '{print $2 $3}' | grep -v cmd | wc -l"""
    process = os.popen(cmd)
    pass_num = process.read()
    process.close()
    print "the passed case number is %s" % pass_num
    pass_num = string.atof(pass_num)

    cmd = """grep -rI "FAILED" ./ | grep "<<" | awk '{print $2 $3}' | grep -v cmd | wc -l"""
    process = os.popen(cmd)
    fail_num = process.read()
    process.close()
    print "the failed case number is %s" % fail_num
    fail_num = string.atof(fail_num)

    cmd = """grep -rI "INCONCLUSIVE" ./ | awk '{print $2 $3}' | grep -v cmd | grep -v '^$' | wc -l"""
    process = os.popen(cmd)
    inclusive_num = process.read()
    process.close()
    print "the inclusive case number is %s" % inclusive_num
    inclusive_num = string.atof(inclusive_num)

    pass_rate = pass_num/(pass_num + fail_num + inclusive_num)*100
    print "the pass rate of anvl test is %.4f%%" % pass_rate
    return pass_rate
	
	
def main():
    dir = resultDir.enterDir()
    calculate(dir)
	
	
if __name__ == '__main__':
    main()
