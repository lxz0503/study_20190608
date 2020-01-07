#!/usr/bin/env python3
# coding=utf-8
# 统计出前N轮比赛每轮都有进球的球员
# 相当于找出多个字典里的公共key

from functools import reduce
from random import randint,sample

# 抽样3到6位球员进球
# a = sample(('suya', 'meisi', 'gelzm', 'wl', 'ronaload', 'aaa', 'bbb'), randint(3, 6))
# print(a)  # ['gelzm', 'suya', 'wl', 'ronaload', 'meisi']
# 生成字典,每一轮比赛球员的进球情况，每轮比赛有3到6名球员进球，每次进1到4个球
r1 = {x: randint(1, 4) for x in sample(('suya', 'meisi', 'gelzm', 'wl', 'ronaload', 'aaa', 'bbb'), randint(3, 6))}
r2 = {x: randint(1, 4) for x in sample(('suya', 'meisi', 'gelzm', 'wl', 'ronaload', 'aaa', 'bbb'), randint(3, 6))}
r3 = {x: randint(1, 4) for x in sample(('suya', 'meisi', 'gelzm', 'wl', 'ronaload', 'aaa', 'bbb'), randint(3, 6))}
# print(r1)  # {'bbb': 4, 'wl': 3, 'ronaload': 1, 'gelzm': 4, 'aaa': 2, 'suya': 3}

# method one,效率低
# res = []
# for k in r1:
#     if k in r2 and k in r3:
#         res.append(k)
# print(res)
print('############## method two #############')
# method two, 用map,reduce,set
# print(r1.keys())
# print(r2.keys())
# a = r1.keys() & r2.keys()
# print(a)
#
# a = map(dict.keys, [r1, r2, r3])
# print(type(a))    # <class 'map'>
print(reduce(lambda x, y: x & y, list(map(dict.keys, [r1, r2, r3]))))