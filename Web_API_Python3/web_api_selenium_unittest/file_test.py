#!/usr/bin/env python
#encoding=UTF-8

s=open("s.txt").read()
print type(s)
#s is a string
print s
#add content to s

s+="\n\n\n"
s+="_WRS_CONFIG_ADDEDCFLAGS=y\n"
s+="_WRS_CONFIG_RTNET=y\n"
print s
