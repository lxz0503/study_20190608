#!/usr/bin/env python3
# coding=utf-8
import pandas as pd

df = pd.read_excel('bug.xls')
test_data = []
for i in df.index.values:     # 获取行号的索引，并对其进行遍历：
    # 根据i来获取每一行指定的数据 并利用to_dict转化成字典
    row_data = df.iloc[i, :].to_dict()   # 字典的key为表头名
    # print(row_data)
    test_data.append(row_data)
print("the final data is {0}".format(test_data))

#
# 默认情况下，pandas 假定第一行为表头 (header)，
# 如果 Excel 不是从第一行开始，header 参数用于指定将哪一行作为表头，
# 表头在 DataFrame 中变成列索引 (column index) ，header 参数从 0 开始，比如第二行作为 header，
# 则：df = pd.read_excel(file_name, header=1)

