#!/usr/bin/env python3
# coding=utf-8

import numpy as np
# 一维数组
c = np.arange(10)
print('{0}维数组:{1}'.format(c.ndim, c))   # [0 1 2 3 4 5 6 7 8 9]
print(np.mean(c))     # 4.5 求平均值
print('average is', np.average(c))
print('total is', np.sum(c))
print('max is', np.max(c))
print('minimum is', np.min(c))
print('ptp is', np.ptp(c))   # 最大值和最小值之差,就是极差
print('中位数 is', np.median(c))   # (4+5)/2=4.5 就是中间元素，如果有偶数个元素，就是中间俩个元素的平均值
print(c.tolist())  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # 转化为列表
print('slice from index 0 to 2: {0}'.format(c[:3]))     # [0 1 2]
print(c[-7::-1])    # [3 2 1 0]    #  从第-7个元素开始，到结束，只要是负数开头的，就默认为反向
print(type(c))     # [0 1 2 3 4 5 6 7 8 9]  区别于列表，元素之间没有逗号
c = np.arange(10, 20, 2)     # start,stop, step
print(c.shape)    # (5,)   各个维度的长度
opening_prices = np.loadtxt(
    'numpy_test/stock_price.csv', delimiter=',',
    dtype='f8',
    usecols=3
)
print('opening prices are', opening_prices)
print('sorted opening prices are', np.sort(opening_prices))

# 多维数组
x = np.array([10, 20, 30])
x1 = np.array([10, 20, 30]).tolist()
print(x.ndim)   # 打印维度, 1维度数组
c = np.array([
    [1, 2, 3]
])
print(c.shape)   # (1, 3)　
print('c数组的维度is {}'.format(c.ndim))    # 2维度数组
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
print(g.ndim)    # 3维数组
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
print('多维数组b的维度是{}'.format(b.ndim))   # 数组维度是3，其实就是看有几个左中括号
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
print(x)    # [1. 2. 3. 4. 5.]
print(x.tolist())   # [1.0, 2.0, 3.0, 4.0, 5.0]

#
s = np.arange(1, 10)
print(s)   # [1 2 3 4 5 6 7 8 9]
print('median', np.median(s))    # 5
print(np.cumsum(s))      # 累加  [ 1  3  6 10 15 21 28 36 45]
print(np.cumprod(s))      # 累乘  [     1      2      6     24    120    720   5040  40320 362880]
mean = np.mean(s)
devs = s - mean    # 离差  是一个数组[-4. -3. -2. -1.  0.  1.  2.  3.  4.]
print('devs', devs)
var = (devs ** 2).mean()   # 方差
print('var', var)      # 6.666666666666667
std = np.sqrt(var)    # 标准差
print('std', std)       # 2.581988897471611


