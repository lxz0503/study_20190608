#!/usr/bin/env python3
# encoding=utf-8
"""
@author:Xiaozhan Li
@Email:lxz_20081025@163.com
@time:3/14/2023 5:20 PM
@project:HCAPI
"""
import pandas as pd
import os

cvs_list = []
for i in os.listdir(os.getcwd()):
    if i.endswith('csv') and i != 'XL710_Perf_Record.csv':
        cvs_list.append(i)
print(cvs_list)

pieces = []
for csv_file in cvs_list:
    frame = pd.read_csv(csv_file)
    pieces.append(frame)

df = pd.concat(pieces, ignore_index=True)
df.to_csv('XL710_Perf_Record.csv', index=False)
df.to_excel('XL710_Perf_Record.xlsx', index=False)
