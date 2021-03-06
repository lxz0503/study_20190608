#! /user/bin/env python3
# coding=utf-8
# 如果有中文字符，注意设置pycharm软件的编码为UTF-8即可,并设置文件编码为UTF-8
# encoding='utf_8_sig',可以解决csv打开是乱码的问题
# https://www.cnblogs.com/batteryhp/p/5006274.html     useful link for pandas

import pandas as pd
import os

f_dir = os.path.dirname(__file__) + '/taobao_data.csv'
df = pd.read_csv(f_dir, delimiter=',', encoding='utf-8')
print('所有csv数据:\n', df)

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
grouped = df['成交量'].groupby(df['位置']).mean()
print('grouped is:\n', grouped)

# 传入多个数组，得到按多列统计的结果
means = df['成交量'].groupby([df['位置'], df['卖家']]).mean()
print('the means is:\n', means)

grouped = df.groupby('位置')
print('上海地区数据:\n', grouped.get_group('上海'))   # 选取某一个分组的数据

# 查看每个分组的size,下面例子统计每个分组中卖家的店铺数目
size_group = df.groupby(['位置', '卖家']).size()
print('每个分组的大小:\n', size_group)

# page126,将列名用作分组,将位置作为索引，按均值汇总
print('将位置作为索引的统计均值:\n', df.groupby('位置').mean())
print('将位置和卖家作为索引的统计均值:\n', df.groupby(['位置', '卖家']).mean())

# 数据分割
df1 = df[30:40][['位置', '卖家']]  # 只显示30-39行数据，保留位置和卖家两列
df2 = df[80:90][['卖家', '销售额']]
p_merge = pd.merge(df1, df2, how='left', on='卖家')  # 指定列名,如果不指定列名，默认会选择列名相同的 卖家 列, how参数取决于需求
print(p_merge)

# 根据索引来合并
df1 = df[:5][['位置', '卖家']]
df2 = df[:5][['价格', '成交量']]
# d_merge = pd.merge(df1, df2, left_index=True, right_index=True)
d_merge = df1.join(df2)   # 效果同上，推荐用这个
# print('merge data based on index:\n', d_merge)

# page 132, concat()轴向连接
s1 = df[:5]['商品']   # 第0到第4行数据
s2 = df[:5]['价格']   # 第0到第4行数据
s3 = df[:5]['成交量']   # 第0到第4行数据
sn = pd.concat([s1, s2, s3], axis=1)
print('the new DataFrame is:\n', sn)

# page 134 数据变形，stack()  unstack(),可以旋转数据的行和列
data = pd.read_csv('hz_weather.csv')
print(data.head())
a = data.stack()
print(a.to_csv('xiaozhan_test.csv', index=True, header=True, encoding='utf_8_sig'))
# page 136
df = pd.read_csv('qunar_free_trip.csv')
# print(df.head())
# # 按出发地，目的地分组生成价格均值汇总表, 只取价格列的平均值，如果不指定取那些列，默认会取所有数值列的平均值
avg_price = df['价格'].groupby([df['出发地'], df['目的地']]).mean()
print(avg_price)
# page 138
df_ = pd.read_csv('qunar_route_cnt.csv')
# print(df_.head())
# 按出发地，目的地分组生成价格均值汇总表,会包含 价格列和节省列，因为这两列都是数值，能求平均值
df1 = df.groupby([df['出发地'], df['目的地']], as_index=False).mean()
print(df1)
# page 139
df2 = pd.pivot_table(df, values=['价格'], index=['出发地'], columns=['目的地'])
print(df2.head())
# 从杭州出发的目的地vs去程方式vs平均价格的数据透视表
df1 = pd.pivot_table(df[df['出发地']=='杭州'], values=['价格'], index=['出发地'], columns=['去程方式'])
print(df1)
# page 140  缺失值，异常值，重复值的处理
df = pd.read_csv('hz_weather.csv')
df1 = pd.pivot_table(df,values=['最高气温'],index=['天气'],columns=['风向'])
print(df1.isnull())
# 使用参数axis=0来删除有缺失值的行
print(df1.dropna(axis=0))
# 使用字符串来代替缺失值
print(df1.fillna('missing'))
# 使用平均数来代替缺失值
print(df1.fillna(df1.mean()))

# 移除重复数据
print('统计重复值:\n', df.duplicated('最高气温').value_counts())
print(df.duplicated('最高气温'))
print(df.drop_duplicates('最高气温'))  # 按照 最高气温 来查找重复数据，例如两行最高气温相同，则只保留第一个最高气温所在的行

# page 155 时序分析
data = pd.read_csv('hz_weather.csv')
df = data[['日期','最高气温','最低气温']]
print(df.head())
# 提取一月份的温度数据
df = df.set_index('日期')   # 先要把日期作为index才能继续下面的判断
df_jan = df[(df.index >= '2017-01-01') & (df.index <= '2017-02-01')]
print('一月份温度数据:\n', df_jan)

# page 157
# page 158 数据类型转换
df_pop = pd.read_csv('european_cities.csv')
print('欧洲人口数据:\n', df_pop.head())
print(type(df_pop.Population[0]))
# 删除人口字段中的逗号, 并新增一列
df_pop['NumericPopulation'] = df_pop.Population.apply(lambda x: int(x.replace(',', '')))
print(df_pop.head())
# 读取state列中前3行
print(df_pop['State'].values[:3])
# remove while space
df_pop['State'] = df_pop['State'].apply(lambda x: x.strip())
print(df_pop['State'].values[:3])
