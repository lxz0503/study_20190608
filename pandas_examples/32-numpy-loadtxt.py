#!/usr/bin/env python3
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

(a, b) = np.loadtxt('numpy_test/test.txt', dtype=str, skiprows=1, comments='#', delimiter=',', usecols=(0, 2), unpack=True)
print(a)   # ['5/1/2015' '6/1/2015' '7/1/2015' '8/1/2015' '9/1/2015']  第0列
print(list(b))   # 第2列, 直接将其转化为列表  ['1', '2', '3', '4', '5']

# 以字符串形式str来读取文本内容，选取第0和第2列
t = np.loadtxt('numpy_test/test.txt', dtype=str, skiprows=1, comments='#', delimiter=',', usecols=(0, 2), unpack=False)
print(t.tolist())   # [['5/1/2015', '1'], ['6/1/2015', '2'], ['7/1/2015', '3'], ['8/1/2015', '4'], ['9/1/2015', '5']]

# 第一行是文字标题，不是int，所以跳过第一行
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
print(np.mean(f))     # 3.5
# 将numpy数据保存到文本,下面是以字符形式，也可fmt='%.1f'
np.savetxt('numpy.txt', f, fmt='%s', delimiter=',', newline='\n', comments='#', header='xiaozhan', footer='test')
