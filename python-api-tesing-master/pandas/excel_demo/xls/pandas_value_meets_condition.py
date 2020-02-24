#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-22 pandas_value_meets_condition.py

import pandas as pd

input_file = "sales_2013.xlsx"
output_file = "pandas_output6.xls"

demo_excel = pd.ExcelFile(r'sales_2013.xlsx')
print(demo_excel.sheet_names)    # ['january_2013', 'february_2013', 'march_2013']
table1 = demo_excel.parse(sheet_name=demo_excel.sheet_names[0])     # 查看每个sheet的内容
print(table1)

data_frame = pd.read_excel(input_file, 'january_2013', index_col=None)
data_frame_value = data_frame[data_frame['Sale Amount'].astype(float) > 1400.0]    # 强制转换为float类型

writer = pd.ExcelWriter(output_file)
data_frame_value.to_excel(writer, sheet_name='jan_13_output', index=False)
writer.save()