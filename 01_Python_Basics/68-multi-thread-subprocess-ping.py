#!/usr/bin/env python3
# coding=utf-8

import subprocess
import threading
import os

def is_reachable(ip):
    cmd = "ping -c 1 " + ip
    process = os.popen(cmd)
    output = process.read()
    process.close()
    if "icmp_req" in output:
        print('{0} is alive'.format(ip))
    else:
        print('{0} is not reachable'.format(ip))


def main():
    with open('ips.txt') as f:
        lines = f.readlines()
        threads = []
        for line in lines:
            thr = threading.Thread(target=is_reachable, args=(line,))
            thr.start()
            threads.append(thr)

        for thr in threads:
            thr.join()

if __name__ == '__main__':
    main()

