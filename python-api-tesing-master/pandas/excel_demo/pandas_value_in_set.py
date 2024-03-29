#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-19 pandas_value_in_set.py
import pandas as pd

input_file = r"supplier_data.csv"
output_file = r"output_files\4output.csv"

data_frame = pd.read_csv(input_file)

# 把符合条件的筛选出来，写到一个文件
# 选择 Purchase Date 在 '1/20/14','1/30/14', : 表示取所有列
important_dates = ['1/20/14', '1/30/14']
data_frame_value_in_set = data_frame.loc[data_frame['Purchase Date'].isin(important_dates), :]

data_frame_value_in_set.to_csv(output_file, index=False)