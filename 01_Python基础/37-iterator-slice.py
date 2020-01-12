#!/usr/bin/env python3
# coding=utf-8
# 对迭代器做切片操作
from itertools import islice

f = open('test_result.log')  # 文件句柄是迭代器
# f.readlines()会一次把所有内容读到内存，如果文件过大，会导致内存不够
# f.seek(0) 让文件指针返回头部
# 读取文件的100到300行
# 没执行一次会消耗f对象，即指针往后移动
for line in islice(f, 100, 300):
    print(line)

for line in islice(f, 500):  # 前500行
    print(line)

for line in islice(f, 100, None):   # 从100行到结束
    print(line)

# test
l = range(20)
t = iter(l)
for x in islice(t, 5, 10):
    print(x)

for x in t:
    print(x)   # start from 10

# official example from python doc
reportlines = ['EuroPython', 'Roster', '', 'alex', '', 'laura', '', 'martin', '', 'walter', '', 'samuele']
for name in islice(reportlines, 3, None, 2):
    print(name.title())


