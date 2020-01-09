#!/usr/bin/env python
#encoding=UTF-8

import os,re

if __name__ == "__main__":

    """pattern="(IPV6.*): (\w+)"
    str="IPV6-1.1: Passed"
    m=re.match(pattern,str)
    print m.group(1)
    print m.group(2)"""
    
    """fp=open("putty_ipv6_host.log",'r')
    
    pass_list=[]
    fail_list=[]
    for line in fp.readlines():
    
        if line.find("Passed")>=0:
            pass_list.append(line.strip("<<").strip("\r\n"))
        if line.find("FAILED")>=0:
            fail_list.append(line.strip("<<").strip("\r\n"))
    #print pass_list
    print "the number of passed case is %d "% len(pass_list)
    print fail_list
    print "the number of failed case is %d" % len(fail_list)"""
    
    #s=sorted(os.listdir(os.getcwd()))
    #directory=[]
    #for i in s:
        #if os.path.isdir(i)>0:
            #directory.append(i)
    #print directory[-1]
    #os.chdir(directory[-1])
    cmd="""grep -rI ".*: Passed" ./ | awk '{print $2 $3}' | grep -v cmd""" 
    process=os.popen(cmd)
    output1=process.read()
    process.close()
    
    cmd="""grep -rI ".*: Passed" ./ | awk '{print $2 $3}' | grep -v cmd | wc -l"""
    process=os.popen(cmd)
    output2=process.read()
    process.close()

    fp_pass = open("test_pass.log",'w')
    fp_pass.write(output1)
    fp_pass.write("\nThe passed case number is:")
    fp_pass.write(output2)
    fp_pass.close()
   

    cmd="""grep -rI "FAILED" ./ | grep "<<" | awk '{print $2 $3}' | grep -v cmd"""
    process=os.popen(cmd)
    output1=process.read()
    process.close()
    
    cmd="""grep -rI "FAILED" ./ | grep "<<" | awk '{print $2 $3}' | grep -v cmd | wc -l"""
    process=os.popen(cmd)
    output2=process.read()
    process.close()

    fp_fail=open("test_fail.log",'w')
    fp_fail.write(output1)
    fp_fail.write("\nThe failed case number is:")
    fp_fail.write(output2)
    fp_fail.close()
    
       
    cmd="""grep -rI "INCONCLUSIVE" ./ | awk '{print $2 $3}' | grep -v cmd"""
    process=os.popen(cmd)
    output1=process.read()
    process.close()

    cmd="""grep -rI "INCONCLUSIVE" ./ | awk '{print $2 $3}' | grep -v cmd | wc -l"""
    process=os.popen(cmd)
    output2=process.read()
    process.close()
   
    fp_inclusive=open("test_inclusive.log",'w')
    fp_inclusive.write(output1)
    fp_inclusive.write("\nThe INCLUSIVE case number is:")
    fp_inclusive.write(output2)
    fp_inclusive.close()
    
    

