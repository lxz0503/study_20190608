#!/usr/bin/env python3
# coding=utf-8
import pandas as pd

# you can use names to set the name of every column, otherwise you use the default column names
df = pd.read_csv('bug_record.csv', header=0)   # read first line, with header
print(df.head(3))
# df.to_excel('record_header.xls', index=False, header=True)   # write data to excel, you can decide if it has header by setting header=True or False
# df.to_csv('record_header.csv', index=False, header=True)

# pandas read csv without header
print('pandas read csv without header')
df = pd.read_csv('bug_record_no_header.csv', header=0, names=['a', 'b', 'c', 'd'])   # read first line, set column names
print(df.head(3))
# df.to_csv('xiaozhan.csv', index=False)   # the default value of header is True

