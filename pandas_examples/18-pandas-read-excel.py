#!/usr/bin/env python3
# coding=utf-8
import pandas as pd

df = pd.read_excel('performance.xls')
test_data = []
for i in df.index.values:     # 获取行号的索引，并对其进行遍历：
    # 根据i来获取每一行指定的数据 并利用to_list转化成列表
    row_data = df.iloc[i, :].to_list()  # this is for pandas v1.0,把每行数据读到一个列表里，默认不包含表头，即第一行
    # print(row_data)
    test_data.append(row_data)
print("最终获取到的数据是：{0}".format(test_data))

# 下面的方法更简单，把每行数据放到列表里面
df = pd.read_excel('performance.xls')
list1 = df.values.tolist()
print(list1)