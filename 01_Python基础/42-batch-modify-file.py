#!/usr/bin/env python3
# coding=utf-8
# 在一个目录下有多个文件，有py结果，sh结尾，c结尾等，而且都没有可执行权限
# 要求，修改所有文件，使其具有可执行权限

import os
import stat
# for f in os.listdir('.'):
#     # endswith()的参数可以是一个元组，但是不能是列表，满足元组其中一条即可，相当于或语句
#     if f.endswith(('.sh', '.py', '.txt')):
#         print(f)
# 简洁代码, 用列表解析方式,3元表达式
all_files = [f for f in os.listdir('.') if f.endswith(('.sh', '.py', '.txt'))]
# print(all_files)
for f in all_files:
    # print(oct(os.stat(f).st_mode))  # 8进制查看权限
    os.chmod(f, os.stat(f).st_mode | stat.S_IXUSR)  
    print(oct(os.stat(f).st_mode))