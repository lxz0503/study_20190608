#! /user/bin/env python3
# coding=utf-8
# 如果有中文字符，注意设置pycharm软件的编码为UTF-8即可,并设置文件编码为UTF-8
# encoding='utf_8_sig',可以解决csv打开是乱码的问题

import pandas as pd
import os

f_dir = os.path.dirname(__file__) + '/taobao_data.csv'
df = pd.read_csv(f_dir, delimiter=',', encoding='utf-8', header=0)
# print('所有csv数据:\n', df)

# 块的选取，选择行和列组成的数据,此处的0:3相当于[0,1,2,3]
print('前4行数据是:\n', df.ix[0:3])
print('前4行数据是:\n', df.ix[0:3, ['商品', '价格']])

# 选择前5行数据，用head()
cols = df[['商品', '价格']]
print('前5行数据是:\n', cols.head())

# 从已有的列中创建一个新的列,直接修改了df,后续的df都会有新的一列数据
df['销售额'] = df['价格'] * df['成交量']
print('成交额前5行数据:\n', df.head())

# 根据条件来过滤行
a = df[(df['价格'] < 100) & (df['成交量'] > 10000)]
print(a)

# encoding='utf_8_sig',可以解决csv打开是乱码的问题
df1 = df.set_index('位置')    # 将某个字段设置为index
df1.to_csv('taobao_price_data_xiaozhan_write.csv', index=True, header=True, encoding='utf_8_sig')
# df1 = df1.sort_index()
df1 = df1.sort_values(by='位置', ascending=True)
# print('按照位置字段排序结果:\n', df1)

# 最好用下面的方法来排序
df2 = df.set_index(['位置', '卖家'])
a = df2.sort_values(by='位置', ascending=True)
print('a is:\n', a)
# 效果如下
# 上海 简港旗舰店                 中老年女装夏装套装加肥加大码T恤上衣妈妈装时尚短袖夏季两件套  ...  1586850.0
#    夏洛特的文艺                中老年女装清凉两件套妈妈装夏装大码短袖T恤上衣雪纺衫裙裤套装  ...  4016870.0
#    佳福妈妈商城           中老年人女装套装妈妈装夏装大码奶奶装40-50岁60短袖T恤70两件套  ...   137808.0
#    简港旗舰店              母亲节衣服夏季中老年女装夏装套装上衣40-50岁妈妈装T恤衫两件套  ...  1478268.0
#    金良国际               母亲节中老年女装夏装短袖40-50岁雪纺衫大码妈妈装T恤宽上衣套装  ...   204036.0

# drop()，默认axis=0是删掉行，axis=1是删掉列
df_mean = df.drop(['商品', '卖家', '销售额'], axis=1).groupby('位置').mean().sort_values('成交量', ascending=False)
print('按位置计算的成交量均值是:\n', df_mean)
df_mean.to_csv('taobao_price_data_xiaozhan_mean.csv', columns=['价格', '成交量'], index=True, header=True, encoding='utf_8_sig')
# sum()
df_sum = df.drop(['商品', '卖家', '销售额'], axis=1).groupby('位置').sum().sort_values('成交量', ascending=False)
print('按位置计算的成交量总和是:\n', df_sum)
df_sum.to_csv('taobao_price_data_xiaozhan_sum.csv', columns=['价格', '成交量'], index=True, header=True, encoding='utf_8_sig')

# 向csv写入数据,with index and header, you can also remove them with setting index=False
df.to_csv('taobao_price_data_xiaozhan.csv', columns=['商品', '价格'], index=False, header=True, encoding='utf_8_sig')

# page No.124
# 将指定字段作为索引，汇总数据
# 按位置分组，并计算成交量列的平均值，
grouped = df['成交量'].groupby(df['位置']).mean() #
print('grouped is:\n', grouped)

grouped = df.groupby('位置')
print(grouped.get_group('上海'))   # 选取某一个分组的数据

# means = df['成交量'].groupby(df['位置'],df['卖家']).mean()
# # print('the means is:\n', means)

a = df.groupby(['位置', '成交量']).size()
print(a)