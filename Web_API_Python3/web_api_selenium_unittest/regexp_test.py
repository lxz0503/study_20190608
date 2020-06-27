"""this is for personal regexp test"""
#!/usr/bin/env python
#encoding=UTF-8

import re

pattern="(?i)Name"  #this means to ignore n or N
string="Name"
m=re.match(pattern,string)

print m.group()

for i in "hello":
    if i=="l":
        break
    print i
    print "aaaa"

l="itl_generic"
list=l.split('_')
#if re.search("itl",l):
 #   print "this is itl"
a="platform"
if a.startswith("platform"):
    print "pp"

b="7"

if b.split('.')[0]=='7':
    print "bbb"
    print b[0]

c="./vxworks-platform/guests/vxworks-7/pkgs_v2/net/ipnet/coreip/src/iptcp/src/iptcp.c"
tmp=c.split("vxworks-platform")[1]
#print tmp.split('src')[0]
print tmp
