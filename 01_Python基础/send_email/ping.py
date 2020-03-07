#!/usr/bin/env python3
# coding = utf-8
import os
import sys


class CheckServer(object):
    def __init__(self, check_cmd):
        self.check_cmd = check_cmd

    def check_anvl(self):
        for cmd in self.check_cmd:
            process = os.popen(cmd)
            output = process.read()
            process.close()
            #print(output)
            # analyze the output
            if "icmp_req" in output:
                print('%s is ok'.format(cmd))
            else:
                print('%s is not ok,error!'.format(cmd))
                sys.exit(1)

    
if __name__ == '__main__':
    check_cmd = ["ping 128.224.166.46 -c 1", "ping 128.224.159.79 -c 1"]
    ts = CheckServer(check_cmd)
    ts.check_anvl()