#!/usr/bin/env python3
# encoding=utf-8

import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.randn(7, 3))
print(f'前三行\n{df.head(3)}')
df.iloc[:4, 1] = np.nan
df.iloc[:2, 2] = np.nan
print(df)
cleaned = df.dropna()
# print(f'after drop NA\n {cleaned}')
# 修改266页代码 NA已经不适用了   use np.nan to replace NA
print(f'fillna\n {df.fillna(0)}')
print(f'fillna\n {df.fillna({1:2, 2:5})}')     # 用字典来填充，第一列NA填充为2，第二列填充为5
# fillna默认会返回新对象，但也可以对现有对象进⾏就地修改
_ = df.fillna(10, inplace=True)
print(df)
# 处理重复行----指的是每行内容完全相同
data = pd.DataFrame({'k1': ['one', 'two'] * 3 + ['two'],
                     'k2': [1, 1, 2, 3, 3, 4, 4]})
# print(data)
# print(data.duplicated())
print('keep the first', data.drop_duplicates())   # 删除重复的行，保留第一个出现的
# print('keep the last', data.drop_duplicates(keep='last'))   # 删除重复的行，保留第一个出现的
# print('remove all duplicated', data.drop_duplicates(keep='False'))   # 删除重复的行，保留第一个出现的
# print(data.drop_duplicates('k1'))   # #删除第一列重复值，返回副本
# print(data.drop_duplicates('k2'))   # #删除第2列重复值，返回副本
# Transforming Data Using a Function or Mapping   p198 or p272
data = pd.DataFrame({'food': ['bacon', 'pulled pork', 'bacon', 'Pastrami', 'corned beef',
                              'Bacon', 'pastrami', 'honey ham', 'nova lox'],
                     'ounces': [4, 3, 12, 6, 7.5, 8, 3, 5, 6]})
# print(data)
meat_to_animal = {
    'bacon': 'pig',
    'pulled pork': 'pig',
    'pastrami': 'cow',
    'corned beef': 'cow',
    'honey ham': 'pig',
    'nova lox': 'salmon'
}
lowercased = data['food'].str.lower()
# print(lowercased)
# Series的map⽅法可以接受⼀个函数或含有映射关系的字典型对象
# Suppose you wanted to add a column indicating the type of animal that each food came from
data['animal'] = lowercased.map(meat_to_animal)
print(data)
#           food  ounces  animal
# 0        bacon     4.0     pig
# 1  pulled pork     3.0     pig
# 2        bacon    12.0     pig
# 3     Pastrami     6.0     cow
# 4  corned beef     7.5     cow
# or you can use lambda, I can not understand below code
# data['food'].map(lambda x: meat_to_animal[x.lower()])
# replace function in series
data = pd.Series([1., -999., 2., -999., -1000., 3.])
# data.replace(-999, np.nan, inplace=True)
data.replace({-999: np.nan, -1000: 0}, inplace=True)
# print(data)
# Renaming Axis Indexes
data = pd.DataFrame(np.arange(12).reshape((3, 4)),
                    index=['Ohio', 'Colorado', 'New York'],
                    columns=['one', 'two', 'three', 'four'])
transform = lambda x: x[:4].upper()   # the first four characters are changed to upper
data.index = data.index.map(transform)
print(data)
#       one  two  three  four
# OHIO    0    1      2     3
# COLO    4    5      6     7
# NEW     8    9     10    11
#
d = data.rename(index=str.title, columns=str.upper)
# print(d)
# rename can be used in conjunction with a dict-like object
data.rename(index={'OHIO': 'INDIANA'},
            columns={'three': 'peekaboo'},
            inplace=True)
print(data)
# Discretization and Binning  离散化 面元----不懂   to process continuous data
ages = [20, 22, 25, 27, 21, 23, 37, 31, 61, 45, 41, 32]
# Let’s divide these into bins of 18 to 25, 26 to 35, 36 to 60, and finally 61 and older
bins = [18, 25, 35, 60, 100]
cats = pd.cut(ages, bins)
# print(cats)
d = pd.value_counts(cats)
print(d)
# (18, 25]     5   圆括号表示开端，⽽⽅括号则表示闭端（包括）
# (35, 60]     3
# (25, 35]     3
# (60, 100]    1
#
data = np.random.rand(20)
cats = pd.cut(data, 4, precision=2)  #
d = pd.value_counts(cats)
print(d)
#
data = np.random.randn(1000)
cats = pd.qcut(data, 4)  #
d = pd.value_counts(cats)
print(d)
# Detecting and Filtering Outliers
# 局外人；门外汉 异常值；异常点
data = pd.DataFrame(np.random.randn(1000, 4))
# 假设你想要找出某列中绝对值⼤⼩超过3的值
col = data[2]   # 第2列
print(col[np.abs(col) > 3])
# 要选出全部含有“超过3或－3的值”的⾏
d = data[(np.abs(data) > 3).any(1)]
print(d)
# 将值限制在区间－3到3以内：
data[np.abs(data) > 3] = np.sign(data) * 3
print(data.head(10))
# 根据数据的值是正还是负，np.sign(data)可以⽣成1和-1
print(np.sign(data).head())
# Permutation and Random Sampling
