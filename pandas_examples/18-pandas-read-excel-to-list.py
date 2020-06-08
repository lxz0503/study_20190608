#!/usr/bin/env python3
# coding=utf-8
import pandas as pd

df = pd.read_excel('performance.xls', sheet_name='IA', header=None)   # 这个表示没有表头，即第一行就是数据,要设置header=None
test_data = []
for i in df.index.values:     # 获取行号的索引，并对其进行遍历：
    # 根据i来获取每一行指定的数据 并利用to_list转化成列表
    row_data = df.iloc[i, :].to_list()  # this is for pandas v1.0,把每行数据读到一个列表里，默认不包含表头，即第一行
    # print(row_data)
    test_data.append(row_data)
print("the final data is {0}".format(test_data))

# 下面的方法更简单，把每行数据放到列表里面
df = pd.read_excel('performance.xls', sheet_name='ARM')    # 默认第一行就是表头，所以没有把表头写到list
list1 = df.values.tolist()
print(list1)

# 处理list的数据，写到一个文本里
with open('xiaozhan.txt', 'w') as f:
    for i in list1:
        f.write(i[0] + ':' + str(i[1]) + '\n')
#
# 默认情况下，pandas 假定第一行为表头 (header)，
# 如果 Excel 不是从第一行开始，header 参数用于指定将哪一行作为表头，
# 表头在 DataFrame 中变成列索引 (column index) ，header 参数从 0 开始，比如第二行作为 header，
# 则：df = pd.read_excel(file_name, header=1)

# next you can refer to 26-pandas-yield-read-txt-to-excel.py which can read data from txt file into excel

