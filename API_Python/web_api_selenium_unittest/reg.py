#!/usr/bin/env python

import os,re

"""pattern="(IPV6.*): (\w+)"
str="IPV6-1.1: Passed"
m=re.match(pattern,str)
print m.group(1)
print m.group(2)"""

fp=open("putty_ipv6_host.log",'r')

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
print "the number of failed case is %d" % len(fail_list)
