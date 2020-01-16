#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-19 pandas_value_meets_condition.py
import pandas as pd

input_file = r"supplier_data.csv"
output_file = r"output_files\3output.csv"

data_frame = pd.read_csv(input_file)

# 字符串处理str.strip('$')，然后强制转换为float类型   astype(float)
data_frame['Cost'] = data_frame['Cost'].str.strip('$').astype('float')
data_frame_value_meets_condition = data_frame.loc[(data_frame['Supplier Name']\
.str.contains('Z')) | (data_frame['Cost'] > 600.0), :]

data_frame_value_meets_condition.to_csv(output_file, index=False)


# 强制类型转换
# df[' Min Humidity']=df[' Min Humidity'].astype('float64')   或者用下面的语句也可以
# df=df.astype({'Max Humidity':'float64','Max Dew PointF':'float64'})