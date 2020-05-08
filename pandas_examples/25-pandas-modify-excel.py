#!/usr/bin/env python3
# coding=utf-8
import pandas as pd

data = pd.read_excel("bug_copy.xls", sheet_name='Sheet1')

# 增加行数据，在第5行新增
# data.loc[8] = ['2/2/2020', 32, 10, 20]

# 增加列数据，给定默认值None
data['profession'] = None

# 保存数据
data.to_excel('bug_copy.xls', sheet_name='Sheet1', index=False, header=True)
