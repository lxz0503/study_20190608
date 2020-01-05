#!/usr/bin/env python3
# coding=utf-8
"""
根据字典中的值，对字典中的项进行排序
"""
from random import randint

# 创建一个字典
grade = {x: randint(60, 100) for x in 'xyzabc'}
# print(grade)
k = grade.keys()   # 返回一个列表，存储字典中所有的key值
v = grade.values()  # 存储字典中所有的value
r = sorted(zip(v, k))   # 按照value从小到大进行排名
print(r)

# 根据value值来排序
l = list(grade.items())
l.sort(key=lambda x: x[1])
print(l)
#
r = sorted(grade.items(), key=lambda x: x[1])
print(r)