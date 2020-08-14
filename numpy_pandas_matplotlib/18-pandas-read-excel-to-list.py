#!/usr/bin/env python3
# coding=utf-8
import pandas as pd

df = pd.read_excel('performance.xlsx', sheet_name='IA', header=None)   # 这个表示没有表头，即第一行就是数据,要设置header=None
print('the original dataframe is \n{}'.format(df))
test_data = []
for i in df.index.values:     # 获取行号的索引，并对其进行遍历：
    # 根据i来获取每一行指定的数据 并利用to_list转化成列表
    row_data = df.iloc[i, :].to_list()  # this is for pandas v1.0,把每行数据读到一个列表里，默认不包含表头，即第一行
    # print(row_data)
    test_data.append(row_data)
print(test_data)
# print("the final data is {0}".format(test_data))
# print(df.iloc[[0, 1]])
print(df[0:2])    # 表示从第一行到第二行的记录。第一行默认从0开始数，不包含末端的2


# 下面的方法更简单，把每行数据放到列表里面
df = pd.read_excel('performance.xlsx', sheet_name='ARM')    # 默认第一行就是表头，所以没有把表头写到list
list1 = df.values.tolist()
print(list1)

# 处理list的数据，写到一个文本里
with open('xiaozhan.txt', 'w') as f:
    for i in list1:
        f.write(i[0] + ':' + str(i[1]) + '\n')

# pandas 读取指定列
# 这个表示没有表头，即第一行就是数据,要设置header=None,可以设定读取哪些列,例如usecols=[0, 5]是第0和第5列，也可以用usecols=['A, F']
# df = pd.read_excel('performance.xlsx', sheet_name='IA', header=None, usecols='A, C')
df = pd.read_excel('performance.xlsx', sheet_name='IA', header=None, usecols=[0, 2], nrows=2)  # nrows=2表示读取前两行数据
print(df)


#
# 默认情况下，pandas 假定第一行为表头 (header)，
# 如果 Excel 不是从第一行开始，header 参数用于指定将哪一行作为表头，
# 表头在 DataFrame 中变成列索引 (column index) ，header 参数从 0 开始，比如第二行作为 header，
# 则：df = pd.read_excel(file_name, header=1)

# next you can refer to 26-pandas-yield-read-anvl-log-to-excel.py which can read data from txt file into excel

# 取第0和第2行，第1和第3列
# df.iloc[[0, 2], [1, 3]]
# df.iloc[[0, 1]]   取第0和第1行,默认所有列
# 取第0到第1行，不包括第二行 df[0:2]

