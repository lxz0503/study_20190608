#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/14/2022 5:44 PM
@file:38-设置索引.py
@project:xiaozhan_git
"""
import pandas as pd

data = {
        'year': [2016, 2017, 2018, 2019],
        'month': [1, 2, 3, 4],
        'price': [50000, 48000, 35000, 30000]
        }    # 每一列数据, 通过字典来创建
# 默认字典的key就是column的名字，也可以自己指定顺序和名字（参数columns），而index名字默认是0 1 2 3
data_frame = pd.DataFrame(data)
# data_frame.set_index(keys=['year'], inplace=True)
data_frame.set_index(keys=['year','month'], inplace=True)
print(data_frame)
# data_frame.to_excel('multi_index.xlsx', index=True)
