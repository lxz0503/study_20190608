#!/usr/bin/env python3
# coding=utf-8
# https://blog.csdn.net/shener_m/article/details/81047669
import pandas as pd
import csv
import os

f_dir = os.path.dirname(__file__) + '/bug_record.csv'
df = pd.read_csv(f_dir, nrows=3)
# print(df)
f_dir_copy = os.path.dirname(__file__) + '/bug_record_copy.csv'
df.to_csv(f_dir_copy, index=False, header=False)    # ????????index?header
print('df is:\n', df)

dates = pd.date_range('2/1/2018', periods=7)
# ts = pd.Series(np.arange(7), index=dates)
ts = pd.Series(dates)
print('ts is:\n', ts)

# process csv,把每一行数据写进一个大的列表里，列表每个元素就是每行的数据
lines = list(csv.reader(open(f_dir)))
header, values = lines[0], lines[1:]
print('value is:', values)
# 字典生成式来生成一个字典
data_dict = {h: v for h, v in zip(header, values)}
print(type(data_dict))
print(data_dict)
