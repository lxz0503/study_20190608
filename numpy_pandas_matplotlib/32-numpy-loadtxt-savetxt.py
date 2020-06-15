#!/usr/bin/env python3
# coding=utf-8
# 用numpy函数来读取和保存文本文件

from matplotlib import pyplot as plt
from datetime import datetime
from matplotlib import dates
import pandas as pd
import numpy as np

(a, b) = np.loadtxt('numpy_test/test.txt', dtype='str', skiprows=1, comments='#', delimiter=',', usecols=(0, 2), unpack=True)
print(a)   # ['5/1/2015' '6/1/2015' '7/1/2015' '8/1/2015' '9/1/2015']  第0列
print(list(b))   # 第2列, 直接将其转化为列表  ['1', '2', '3', '4', '5']

# 以字符串形式str来读取文本内容，选取第0和第2列
t = np.loadtxt('numpy_test/test.txt', dtype=str, skiprows=1, comments='#', delimiter=',', usecols=(0, 2), unpack=False)
print(t.tolist())   # [['5/1/2015', '1'], ['6/1/2015', '2'], ['7/1/2015', '3'], ['8/1/2015', '4'], ['9/1/2015', '5']]

# 第一行是文字标题，不是int，所以跳过第一行,dtype='i4'表示4字节整数
t = np.loadtxt('numpy_test/data.csv', dtype=int, skiprows=1, comments='#', delimiter=',', unpack=False)
print(t)    # 结果可以用切片来查看
print(t[2])    # [ 80  90 100] 表示取第2行，下标从第0行开始
print(t[[0, 2]])   # 取第0行和第2行
print(t[1:])
print(t[:, [0, 2]])  # 表示去所有行的第0和第2列
print(t[1, 2])   # 取坐标第1行第2列的一个数值

#
f = np.array([
    [1, 2, 3],
    [4, 5, 6]
])
print('数组维度is:', f.ndim, ',平均值is', np.mean(f))     # 3.5
# 将numpy数据保存到文本,下面是以字符形式，也可fmt='%.1f'，也可以整数fmt='%d
np.savetxt('numpy.txt', f, fmt='%d', delimiter=',', newline='\n', comments='#', header='xiaozhan', footer='test')
# #xiaozhan
# 1,2,3
# 4,5,6
# #test
#
f = np.arange(1, 10).reshape(3, 3)
print(f, '数组维度is', f.ndim)
# [[1 2 3]   外层有两个左中括号，所以是二维数组
#  [4 5 6]
#  [7 8 9]]
#
t = np.loadtxt('numpy_test/xiaozhan.txt', dtype='str', comments='#', delimiter=':', unpack=False)
print(t)
# [['tcp_64' '80']
#  ['tcp_1024' '940']
#  ['tcp_65536' '940']
#  ['udp_1400' '955']]
print(t[0][0], '----', t[0][1])     # tcp_64-----80
print(int(t[0][1]))     # <class 'numpy.str_'> 转化为整型int
# stock price
# 日期可以作为字符串
# 或者用numpy的专用处理M8[D]，精确到天,格式按年月日顺序
