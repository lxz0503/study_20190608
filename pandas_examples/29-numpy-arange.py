#!/usr/bin/env python3
# coding=utf-8

import numpy as np
# 一维数组
c = np.arange(10)
print(type(c))     # [0 1 2 3 4 5 6 7 8 9]  区别于列表，元素之间没有逗号
c = np.arange(10, 20, 2)     # start,stop, step
print(c.shape)
# 多维数组
f = np.array([
    [1, 2, 3],
    [4, 5, 6]
])
print(f.shape)    # (2, 3)

g = np.array([
    [np.arange(1, 5)],
    [np.arange(13, 17)]
])
print(g)  # 两页，每页有一行，每行有4个元素
# [[[ 1  2  3  4]]
#  [[13 14 15 16]]]
print(g[0])   # [[1 2 3 4]]    # 取第0页
print(g[0][0])  # [1 2 3 4]   第0页第0行
print(g[0][0][0])   # 1
print(g.shape)   # (2, 1, 4)  表示这是两页，每页有一行，每行有4个元素
# 遍历数组中每个元素
for i in range(g.shape[0]):
    for j in range(g.shape[1]):
        for k in range(g.shape[2]):
            print(g[i][j][k])
#
h = g.astype(str)
print(h.dtype)
h = g.astype(float)
print(h.dtype)


