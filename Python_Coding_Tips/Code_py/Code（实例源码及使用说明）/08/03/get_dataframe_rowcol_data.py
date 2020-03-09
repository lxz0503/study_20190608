#!/usr/bin/env python3
# coding=utf-8

import pandas as pd

aa = '../data/TB2018.xls'
# df = pd.DataFrame(pd.read_excel(aa))
df = pd.read_excel(aa)
print('------------------按行选取数据-----------------')
print(df[0:1])	 # 第0行
print(df[:5])	 # 第5行之前的数据（不含第5行）
print(df[1:5])   # 第1行到第4行（不含第5行）
print(df[-1:])   # 最后一行
print(df[-3:-1])  # 倒数第3行到倒数第1行（不包含最后1行即倒数第1行）

print('------------------按列选取数据-----------------')
df1 = df[['买家会员名', '买家实际支付金额', '订单状态']]    # 选取多列，多列名字要放在list里
print(df1.head(5))


print('------------------按行列的综合选取数据-----------------')
# 选取某一行（如第2行）的“买家会员名”和“买家实际支付金额”
print(df.loc[[2], ['买家会员名', '买家实际支付金额']])
# 选取第2、3行的“买家会员名”和“买家实际支付金额”
print(df.loc[[2, 3], ['买家会员名', '买家实际支付金额']])
# 如果列名太长可以使用iloc方法
print(df.iloc[0:3, [0, 3, 4, 5]])

print('------------------')
# 另外可以使用at方法选取“买家会员名”列的第3行数据
print(df.at[3, '买家会员名'])
# 使用索引代替列名
print(df.iat[3, 0])
