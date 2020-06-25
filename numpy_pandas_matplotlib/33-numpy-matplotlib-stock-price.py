#!/usr/bin/env python3
# coding=utf-8
# 用numpy函数来读取和保存文本文件
# 文件内容如下
# AAPL,20-01-2011, , 344.17,344.4,333.10,336.2,2000888
# AAPL,21-01-2011, , 342.17,347.4,334.10,337.2,2000999
# AAPL,22-01-2011, , 343.17,349.4,328.10,338.2,2000555

from matplotlib import pyplot as plt
from datetime import datetime
from matplotlib import dates as md
import pandas as pd
import numpy as np

def dmy2ymd(dmy):
    dmy = str(dmy, encoding='utf-8')
    # print(dmy)    # b'20-01-2011'    20-01-2011
    date = datetime.strptime(dmy, '%d-%m-%Y').date()   # 如果不加date()函数，后面会有小时分钟秒全为0
    # print(type(date), '====', date)  # 这是datetime类型，不是字符串类型
    ymd = date.strftime('%Y-%m-%d')    # this str字符串类型
    # print(type(ymd), '---', ymd)
    # wday = date.weekday()   # 0 1 2 3 4 5 6 分别对应周一到周日
    return ymd

numpy_dates, opening_prices, highest_prices, lowest_prices, closing_prices = np.loadtxt(
    'numpy_test/stock_price.csv', delimiter=',',
    dtype='M8[D],f8,f8,f8,f8', converters={1: dmy2ymd},    # 1表示转换第1列
    usecols=(1, 3, 4, 5, 6), unpack=True
)
print(numpy_dates)

plt.figure('Stock Prices for Apple', facecolor='lightgray')
plt.title('Stock Prices for Apple')
plt.xlabel('Date', fontsize=10)
plt.ylabel('Price', fontsize=10)
ax = plt.gca()
# 在水平轴上用的主定位器，次定位器，格式化器
ax.xaxis.set_major_locator(md.WeekdayLocator(byweekday=md.MO))
ax.xaxis.set_minor_locator(md.DayLocator())
ax.xaxis.set_major_formatter(md.DateFormatter('%d %b %Y'))  # 天，月份，年
plt.tick_params(labelsize=10)     # 设置字体
plt.grid(linestyle=':')
# 把numpy的日期类型M8[D]转换为matplotlib的日期类型
dates = numpy_dates.astype(md.datetime.datetime)
# print(dates)
#
rise = closing_prices - opening_prices >= 0.01
print('rise is', type(rise), rise)  # [False False False False False False False False False False False  True True  True  True]
fall = opening_prices - closing_prices >= 0.01
print('fall is', fall)
print('dates size', dates.size)
fc = np.zeros(dates.size, dtype='3f4')  # 每一个元素都是3个浮点数组成
print('fc is', type(fc), fc.ndim, fc)
ec = np.zeros(dates.size, dtype='3f4')
fc[rise], fc[fall] = (1, 1, 1), (0, 0.5, 0)     # 设置颜色，不明白
ec[rise], ec[fall] = (1, 0, 0), (0, 0.5, 0)     # 同上
print('fc', fc)
plt.bar(dates, highest_prices - lowest_prices, 0,
        lowest_prices, color=fc, edgecolor=ec)
plt.bar(dates, closing_prices - opening_prices, 0.5,
        opening_prices, color=fc, edgecolor=ec)
plt.show()

# Simple bar chart with matplotlib
# x = numpy_dates
# x = [i for i in range(15)]
# y = highest_prices
x = ["a", "b", "c", "d", "e"]
y = [20, 10, 30, 25, 15]
plt.title('simple bar')
plt.xlabel('x data')
plt.ylabel('y data')
plt.bar(x, y, alpha=0.5, width=0.3, color='yellow', edgecolor='red', label='highest price', lw=3)
plt.xticks(rotation=45)
plt.show()