import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

cities_prices = {'beijing': 60000, 'shanghai': 59000, 'shenzhen': 58000}  # use dictionary
list_prices = ['beijing', 'shanghai', 'shenzhen']                 # use list
apts = pd.Series(cities_prices)  # index is the key of the dictionary
result = pd.Series(list_prices)
# print("old values: %s" % apts['shanghai'])
# print("old values:", apts['shanghai'])
print(apts)
arrySer = pd.Series(np.arange(10, 15), index=['a', 'b', 'c', 'd', 'e'])  # use array
print('the series is:\n', arrySer)
arrySer.plot.bar()
# arrySer.plot.line()
# arrySer.plot.pie()
plt.show()        # plot

print("the index is %s" % arrySer.index)
print("the value is %s" % arrySer.values)

print(arrySer[0:2])
print(arrySer.iloc[0:2])   # get value from row 0 to 1

print(arrySer[['a', 'b']])
print(arrySer[['a']])
print(arrySer.loc[['a', 'b']])    # get value from index a to b

print(arrySer[arrySer.values < 14])  # get elements that value<10

print(arrySer[arrySer.index != 'a'])  # get elements that index!=a

print(arrySer.describe())      # print overall statistic information

print(arrySer.mean())     # 平均值
print(arrySer.sum())      # 求和
print(arrySer.value_counts())     # 统计每个数值出现的次数

print(arrySer.drop('a'))     # delete index=a这一行

test = arrySer + arrySer  # sum of 2 series
print(test)

# print(type(apts))
# print(apts['beijing'])
# print(apts[['beijing', 'shanghai']])
# print(apts[apts < 60000])
# apts[apts < 60000] = 40000
# print(apts/2)
# print(np.square(apts))

# time series

#创建间隔为1s总数10个时间序列
rng=pd.date_range('20180901',periods=10,freq='S')
#以时间序列为索引值，创建Series
ts=pd.Series(np.random.randint(0,500,len(rng)),index=rng)
#创建间隔为1天总数5个时间序列
rng=pd.date_range('9/1/2018 00:00',periods=5,freq='D')
print(rng)

# 日期格式转换
t = pd.to_datetime('01/05/2019', format='%m/%d/%Y')
print(t)      # 2019-01-05 00:00:00



