#!/usr/bin/env python3
# coding=utf-8

import subprocess
# 复杂用法，执行复杂命令
def run_cmd(command):
    ret = subprocess.Popen(command,   # command是字符串类型参数
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    output = ret.stdout.read() + ret.stderr.read()
    return str(output, encoding='utf-8')    # 家里mac,win7需要用GBK编码


if __name__ == '__main__':
    result = run_cmd("ls -al")     # 传入的参数是一个字符串,shell 命令可以分号分割传入 uname -a;echo 'hello'
    print("命令执行结果是",  result)
    # result = run_cmd("uname -a;echo 'hello'")# 最常见的用法如下,获取某个系统命令的输出
    # 简单用法如下
    # ret = subprocess.getoutput('ls -l')
    # print(ret)
    # retcode, output = subprocess.getstatusoutput('ls -l /test')
    # print(retcode)       # 2
    # print(output)        # ls: 无法访问/test: 没有那个文件或目录