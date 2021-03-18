#!/usr/bin/env python3
# encoding=utf-8

import pandas as pd

name1880 = pd.read_csv('babynames/yob1880.txt', names=['name', 'sex', 'births'])
# print(name1880[:5])
# total_births = name1880.groupby('sex').births.sum()  # 统计男女分别总共出生人数
# 所有文件合并成一个大文件，因为每个文件格式相同
years = range(1880, 1883)
pieces = []
columns = ['name', 'sex', 'births']

for year in years:
    path = 'babynames/yob%d.txt' % year
    frame = pd.read_csv(path, names=columns)

    frame['year'] = year
    pieces.append(frame)
# 将所有数据整合到单个DataFrame中
names = pd.concat(pieces, ignore_index=True)
print(names[:5])
total_births = names.pivot_table('births', index='year', columns='sex', aggfunc=sum)
print(total_births.tail())
#
def add_prop(group):
    # 整数除法会向下圆整
    births = group.births.astype(float)

    group['prop'] = births / births.sum()
