#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-22 pandas_value_matches_pattern.py

import pandas as pd

input_file = "sales_2013.xlsx"
output_file = "pandas_output.xls"

data_frame = pd.read_excel(input_file, 'january_2013', index_col=None)   # 第二个参数是sheet名字

data_frame_column_by_index = data_frame.iloc[:, [1, 4]]      # 取所有行，只取第1和第4列

writer = pd.ExcelWriter(output_file)
data_frame_column_by_index.to_excel(
    writer, sheet_name='jan_13_output', index=False)    # 第二个参数是sheet名字
writer.save()