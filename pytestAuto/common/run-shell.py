#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:1/15/2024 3:57 PM
@file:run-shell.py
"""
import os


def run_shell_cmd1(cmd, retString=True, debug=False):

    process = os.popen(cmd)
    res = process.readlines()   # read into a list
    process.close()
    if debug:
        print('\n=== %s' % cmd)
        print(res)
    # while '\n' in res:
    #     res.remove('\n')
    res = [i.rstrip('\n').strip() for i in res if i != '\n']
    return res


def run_shell_cmd2(cmd, retString=True, debug=False):

    process = os.popen(cmd)
    res = process.read()        # read into string
    process.close()
    if debug:
        print('\n=== %s' % cmd)
        print(res)
    # while '\n' in res:
    #     res.remove('\n')
    res = res.split('\n')
    return list(filter(lambda x: x != '', map(lambda x: x.strip(), res)))


if __name__ == "__main__":
    print(run_shell_cmd1('ifconfig'))
    print(run_shell_cmd2('ifconfig'))
