#!/usr/bin/env python3
# coding=utf-8

import tushare as ts

print(ts.__version__)
pro = ts.pro_api()
df = pro.daily(ts_code='000001.SZ', start_date='20200618', end_date='20200625')
print(df)