#!/usr/bin/env python3
# coding=utf-8
# 实现了把一列数据变成多行
import pandas as pd

file_path = 'user-input.xlsx'
df = pd.read_excel(file_path)
# print(df)
merge_names = list(df.loc[:, "Supplier":].columns.values)
# print(merge_names)
def merge_cols(x):
    # x is a series, 类似于字典
    # remove empty columns
    x = x[x.notna()]
    y = x.values
    # 合并后的列表，每个元素是"Supplier" + "Supplier PN"对
    result = []
    for idx in range(0, len(y), 2):
        result.append(f"{y[idx]}|{y[idx+1]}")      # 用|分隔Supplier和Supplier PN
    return '#'.join(result)    # 所有两两对，用#分隔，返回一个大字符串

# 添加新列，把待合并的所有列变成一个大字符串
df['merge'] = df.loc[:, 'Supplier':].apply(merge_cols, axis = 1)
# 删除不需要的列
df.drop(merge_names, axis=1, inplace=True)   # inplace表示原地删除
# 使用explode把一列变成多行
df['merge'] = df['merge'].str.split('#')   # explode能处理列中元素为列表的形式
df_explode = df.explode('merge')
# 取两列数据，注意str的用法，没有会报错
df_explode['Supplier'] = df_explode['merge'].str.split('|').str[0]
df_explode['Supplier PN'] = df_explode['merge'].str.split('|').str[1]
# 删除merge这一列, axis=1表示按列删除
df_explode.drop('merge', axis=1, inplace=True)
# 把新数据写到excel
df_explode.to_excel('user-output.xlsx', index=False)

