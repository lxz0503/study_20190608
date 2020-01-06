#!/usr/bin/env python3
# https://www.jianshu.com/p/50fb023f208c
import pandas as pd
import numpy as np

# 定义一个字典，每个字典元素对应一个列表,key对应这frame的每一列的名字
ipl_data = {'Team': ['Riders', 'Riders', 'Devils', 'Devils', 'Kings',
            'kings', 'Kings', 'Kings', 'Riders', 'Royals', 'Royals', 'Riders'],
            'Rank': [1, 2, 2, 3, 3, 4, 1, 1, 2, 4, 1, 2],
            'Year': [2014, 2015, 2014, 2015,2014,2015,2016,2017,2016,2014,2015,2017],
            'Points': [876, 789, 863, 673, 741,812,756,788,694,701,804,690]}
df = pd.DataFrame(ipl_data, index=list('123456789999'))   # default index is starting from 0
print('the original data frame is:\n', df)    # default index is 0,1,2....
print(df.groupby('Team').groups)
grouped = df.groupby('Team')
for name, group in grouped:
    print(name)
    print(group)
# 使用get_group（）方法，我们可以选择一个组
print('the group of Devils is:\n', grouped.get_group('Devils'))

# 聚合函数返回每个组的单个聚合值。一旦创建了group by对象，就可以对分组数据执行多个聚合操作。
# 通过agg方法来实现aggregation
grouped = df.groupby('Year')
print('the avg of every year is:\n', grouped['Points'].agg(np.mean))

# 每个组大小的另一种方法是应用size()函数

grouped = df.groupby('Team')
print(grouped.agg(np.size))
print(grouped['Points'].agg([np.sum, np.mean, np.std]))

# 过滤数据
print(df.groupby('Team').filter(lambda x: len(x) >= 3))

# 定义frame，可以设置index或者用默认index
frame = pd.DataFrame([[1,2,3,4], [5,6,7,8], [-10,11,12,-13]],
                     index=['tcp_64', 'tcp_1024', 'udp'],
                     columns=['SR620', 'SR630', 'three', 'four'])
print('data with defined index:\n', frame)
# data with defined index:
#            SR620  SR630  three  four
# tcp_64        1      2      3     4
# tcp_1024      5      6      7     8
# udp         -10     11     12   -13