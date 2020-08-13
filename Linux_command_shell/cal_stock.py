#!/usr/bin/env python3
# coding=utf -8

import pandas as pd

df = pd.read_csv('stock_trend', delimiter=',')
# print(df)
print('My biggest loss is {:.2f}'.format(df['gain'].min()))
print('My biggest gain is {:.2f}'.format(df['gain'].max()))
print('My total gain is {:.2f}'.format(df['gain'].sum()))
print('My avg gain each day from 2020-07-15 to today is {:.2f}'.format(df['gain'].mean()))
# df.to_excel('stock.xlsx', index=None)
