#!/usr/bin/env python
#encoding=UTF-8

import getopt,sys


def test():
    pass

def main():
    test()

if __name__ == "__main__":
    main()
    #print sys.argv[1:]
    options,args=getopt.getopt(sys.argv[1:],"hi:p:",["help","ip=","port="])
    #print type(options)
    #print options
    for i in options:
        print i
    for name,value in options:
        if name in ("-h","--help"):
            pass
        if name in ("-i","--ip"):
            pass
            #print "ip is ",value
        if name in ("-p","--port"):
            pass
            #print "port is ",value
   
