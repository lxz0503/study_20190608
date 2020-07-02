#!/usr/bin/env python3
# coding=utf-8
import pandas as pd

# you can use names to set the name of every column, otherwise you use the default column names
# header参数，是否读取列名，默认读取
df = pd.read_csv('bug_record.csv', skiprows=[1, 2], header=None)   # read first line, with header
print(df)
# df.to_excel('record_header.xls', index=False, header=True)
# write data to excel, you can decide if it has header by setting header=True or False
# df.to_csv('record_header.csv', index=False, header=True)

# pandas read csv without header
print('pandas read csv without header')
df = pd.read_csv('bug_record_no_header.csv', header=0, names=['a', 'b', 'c', 'd'])   # read first line, set column names
print(df.head(3))
# df.to_csv('xiaozhan.csv', index=False)   # the default value of header is True
# read with chunksize
print('====================read with chunksize:======================:')
df = pd.read_csv('bug_record.csv', header=0, chunksize=2)
for t in df:
    print(t)
    t.drop(columns=['Closed'], axis=1, inplace=True)  # 删除某一列数据
    print(t)
# read csv
df = pd.read_csv("1.csv", header=None)   # 不读取列名
print("df:")
print(df.head())

print("df.head():")
print(df.head())      # head(self, n=5)，默认为5行，类似的有tail
print("df.tail():")
print(df.tail())

df = pd.read_csv("1.csv")     # 默认读取列名
print("df:")
print(df.head())

df = pd.read_csv("1.csv", names=['号码', '群号'])    # 自定义列名
print("df:")
print(df.head())

# 自定义列名，去掉第一行
df = pd.read_csv("1.csv", skiprows=[0, 1], names=['号码', '群号'])
print("df:")
print(df.head())


#


