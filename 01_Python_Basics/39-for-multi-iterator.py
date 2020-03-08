#!/usr/bin/env python3
# coding=utf-8
# https://www.cnblogs.com/haiyan123/p/9804091.html    关于itertools模块，学习
from random import randint
# 40人的班级，语文成绩,用列表解析来生成成绩列表
chinese = [randint(60, 100) for i in range(40)]
math = [randint(60, 100) for i in range(40)]
english = [randint(60, 100) for i in range(40)]

total = []
for c, m, e in zip(chinese, math, english):  # 并行操作
    total.append(c + m + e)
# print(total)
# 4个班，考试成绩存储在4个列表
# 一次迭代每个列表，统计成绩高于90的人数
from itertools import chain
c1 = [randint(60, 100) for i in range(42)]
c2 = [randint(60, 100) for i in range(42)]
c3 = [randint(60, 100) for i in range(42)]
c4 = [randint(60, 100) for i in range(42)]
count = 0
for s in chain(c1, c2, c3, c4):   # 将多个可迭代序列连接起来组成一个大的可迭代序列
    if s > 90:
        count += 1
print(count)
print(list(chain(c1, c2, c3, c4)))
#  下面的方法也可以，不过只是用于列表这种可迭代序列
count = 0
t = c1 + c2 + c3 + c4
# print(t)   # print(list(chain(c1, c2, c3, c4))),两者效果相同，都是合并了几个可迭代序列
for s in t:
    if s > 90:
        count += 1
print(count)







