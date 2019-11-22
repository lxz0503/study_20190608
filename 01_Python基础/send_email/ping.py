#!/usr/bin/env python3
import os

def check_anvl():
    ANVL_STATUS=False
    cmd = "ping 128.224.166.46 -c 1"
    process = os.popen(cmd)
    output = process.read()
    process.close()
    #print(output)
    # analyze the output
    if "icmp_req" in output:
        return "anvl server is ok"
        #ANVL_STATUS=True
    else:
        return "anvl server is not available"
    
    
if __name__ == '__main__':
    r = check_anvl()
    print(r)
