#!/usr/bin/env python3
# coding=utf-8
# 从excel中读取数据并显示，通过header和names参数指定column名字
import pandas as pd
import os

# read data from excel
f_dir = os.path.dirname(__file__) + '/performance.xls'
result = pd.read_excel(f_dir, sheet_name='ARM', header=None, names=['config', 'result'])
# print(result)

# write DataFrame into excel with defined column names
data = {
        'city': ['beijing', 'shanghai', 'shenzhen', 'guangzhou'],
        'year': [2016, 2017, 2018, 2019],
        'house_price': [50000, 48000, 35000, 30000]
        }    # 每一列数据

data_frame = pd.DataFrame(data, columns=['year', 'city', 'house_price'])
data_frame1 = pd.DataFrame(data, columns=['year', 'city', 'house_price'])

w_dir = os.path.dirname(__file__) + '/write_excel.xls'
with pd.ExcelWriter(w_dir) as writer:
    data_frame.to_excel(writer, sheet_name='Sheet1', index=False)   # if you don't want index like 0 1 2 3
    data_frame1.to_excel(writer, sheet_name='Sheet2')               # with default index like 0 1 2 3

# read data from another file and write it to excel
data = pd.read_csv('test_result.log', sep=':')
# print(data.head())
data.to_excel('test_result.xlsx', sheet_name='result', index=False)

