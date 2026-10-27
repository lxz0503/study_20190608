#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 3/23/2023 11:37 AM
# @Email = lxz_20081025@163.com
# @Name = IPERF_RESULT_TRIAL.py

import pandas as pd

df_list = pd.read_html('http://pek-vx-nwk1/date/2023-03-19', skiprows=[0])   # this is a list which includes DataFrame
cols = ['Num', 'Board', 'Bits', 'BSP', 'CPU', 'Mode', 'TCP_64_baseline', 'TCP_64', 'TCP_1024_baseline',
        'TCP_1024', 'TCP_65536_baseline', 'TCP_65536', 'UDP_1400_baseline',
        'UDP_1400', 'Spin', 'Run_date']
# specify column names and compose a data frame list
res = []
for df in df_list:
    df.columns = cols
    df.drop(columns=['CPU', 'TCP_64_baseline', 'TCP_1024_baseline', 'TCP_65536_baseline', 'UDP_1400_baseline'],
            inplace=True)
    res.append(df)
# merge two data frames into a new one,
df = pd.concat(res, ignore_index=True)
df.to_excel('IPERF_DAILY_RESULT.xlsx', index=False)
df.to_csv('IPERF_DAILY_RESULT.csv', index=False)
