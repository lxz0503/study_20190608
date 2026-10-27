#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/24/2022 6:19 PM
@file:test_concat.py
@project:xiaozhan_git
"""
import os
import pandas as pd

# path = 'demodata/'
# filesnames = os.listdir(path)
# filesnames = [f for f in filesnames if f.lower().endswith(".xlsx")]
# df_list = []
# for filename in filesnames:
#     df_list.append(pd.read_excel(path + filename))
#
# pd.concat(df_list)

# xiaozhan
# pd.concat函数适合拼接结构完全一样,即列名完全相同的数据结构
df1 = pd.read_excel('demodata/001513_回测结果.xlsx').head()
# print(df1)
df2 = pd.read_excel('demodata/002190_回测结果.xlsx').head()
# print(df2)
df = pd.concat([df1,df2],ignore_index=True)
print(df)

# 把数据保存到zip压缩文件
compression_opts = dict(method='zip',archive_name='out.csv')
df1.to_csv('out.zip', index=False,encoding='utf_8_sig',compression=compression_opts)