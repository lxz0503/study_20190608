#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 3/20/2023 3:30 PM
# @Email = lxz_20081025@163.com
# @Name = IPERF_RESULT_CSV.py
import pandas as pd

df = pd.read_html('http://pek-vx-nwk1/date/2023-03-19', skiprows=[0])[0]
# print(df)
# print(type(df))  # this is a list which includes  <class 'pandas.core.frame.DataFrame'>

cols = ['Num', 'Board', 'Bits', 'BSP', 'CPU', 'Mode', 'TCP_64_baseline', 'TCP_64', 'TCP_1024_baseline',
        'TCP_1024', 'TCP_65536_baseline', 'TCP_65536', 'UDP_1400_baseline',
        'UDP_1400', 'Spin', 'Run_date']
df.columns = cols
df.drop(columns=['CPU', 'TCP_64_baseline', 'TCP_1024_baseline', 'TCP_65536_baseline', 'UDP_1400_baseline'],
        inplace=True)

df.to_excel('IPERF_DAILY_RESULT.xlsx', index=False)
df.to_csv('IPERF_DAILY_RESULT.csv', index=False)
# try below code for

