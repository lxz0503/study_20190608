#!/usr/bin/env python3
# coding=utf-8

import numpy as np
# 一维数组
c = np.arange(10)
print(c)   # [0 1 2 3 4 5 6 7 8 9]
print(np.mean(c))     # 4.5 求平均值
print(c.tolist())  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # 转化为列表
print('slice from index 0 to 2: {0}'.format(c[:3]))     # [0 1 2]
print(c[-7::-1])    # [3 2 1 0]    #
print(type(c))     # [0 1 2 3 4 5 6 7 8 9]  区别于列表，元素之间没有逗号
c = np.arange(10, 20, 2)     # start,stop, step
print(c.shape)    # (5,)

# 多维数组
x = np.array([10, 20, 30])
x1 = np.array([10, 20, 30]).tolist()
print(x.ndim)   # 打印维度, 1维度数组, 只有使用array采用这个ndim维度,np.arange没有
c = np.array([
    [1, 2, 3]
])
print(c.shape)   # (1, 3)　
print(c.ndim)    # 2维度数组
#
f = np.array([
    [1, 2, 3],
    [4, 5, 6]
])
print(np.mean(f))     # 3.5
f1 = f.tolist()   # 数组转化为列表
print(f1)    # [[1, 2, 3], [4, 5, 6]]
f2 = np.array(f1)   # list转化为数组
print(f2)
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
            pass
            # print(g[i][j][k])
#
h = g.astype(str)
print(h.dtype)
h = g.astype(float)
print(h.dtype)
# 构造一个多维数组
b = np.arange(1, 25).reshape(2, 3, 4)   # 2*3*4=24个元素
print(b)
# [[[ 1  2  3  4]
#   [ 5  6  7  8]
#   [ 9 10 11 12]]
#
#  [[13 14 15 16]
#   [17 18 19 20]
#   [21 22 23 24]]]
print(b[:, 0, 0])    # [1 13]
print(b[0])    # [1 13],   you can also use b([0, :, :])
print(b[0, 1])     # [5 6 7 8]，you can also use b[0, 1, ::]
# 按垂直和水平方向堆叠数组组成新的数组
a = np.arange(11, 20).reshape(3, 3)
b = np.arange(21, 30).reshape(3, 3)
c = np.vstack((a, b))   # 按垂直
print(c)
d = np.hstack((a, b))    # 水平方向堆叠
print(d)
# 按垂直方向拆分数组
a, b = np.vsplit(c, 2)
print(a, b, sep='\n')
# 按水平方向拆分数组
a, b = np.hsplit(d, 2)
print(a, b, sep='\n')
#
c = np.row_stack((a, b))   # np.vstack((a, b))
print(c)
# [[11 12 13]
#  [14 15 16]
#  [17 18 19]
#  [21 22 23]
#  [24 25 26]
#  [27 28 29]]
#
d = np.column_stack((a, b))   # np.hstack((a, b))
print(d.size)     # 元素个数18
# 等差数列
x = np.linspace(1, 5, 5)  # 从1到5，分成5份，注意包括5
print(x)
print(x.tolist())   # [1.0, 2.0, 3.0, 4.0, 5.0]

