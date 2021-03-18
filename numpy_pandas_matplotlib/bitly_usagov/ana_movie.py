#!/usr/bin/env python3
# encoding=utf-8

import pandas as pd

# user names
unames = ['user_id', 'gender', 'age', 'occupation', 'zip']
users = pd.read_table('users.dat', sep='::', header=None, names=unames, engine='python')
# ratings
rnames = ['user_id', 'movie_id', 'rating', 'timestamp']
ratings = pd.read_table('ratings.dat', sep='::', header=None, names=rnames, engine='python')
# movie names
mnames = ['movie_id', 'title', 'genres']
movies = pd.read_table('movies.dat', sep='::', header=None, names=mnames, engine='python')
#
# print(users[:5])
# print(ratings[:5])
# print(movies[:5])
# merge tables
data = pd.merge(pd.merge(ratings, users), movies)
print(data[:5])
# data.to_csv('data.csv')
# 修改第43页代码如下,用index和columns替代原来的rows和cols参数
mean_ratings = data.pivot_table('rating', index='title', columns='gender', aggfunc='mean')
# print(mean_ratings[:5])
# mean_ratings.to_excel('a.xlsx')     # store data into excel
# mean_ratings.to_csv('a.csv')
# 过滤掉评分数据不够250条的电影
ratings_by_title = data.groupby('title').size()
print(ratings_by_title[:5])
active_titles = ratings_by_title.index[ratings_by_title >= 250]
# print(active_titles[:5])     # this is an index
# 修改44页代码，ix函数已经被loc或者iloc替代
# https://blog.csdn.net/qq_41913559/article/details/107561309?utm_medium=distribute.pc_relevant.none-task-blog-baidujs_title-1&spm=1001.2101.3001.4242
mean_ratings = mean_ratings.loc[active_titles]
# print(mean_ratings[:5])
# mean_ratings.to_excel('mean_ratings.xlsx')
# 女性最喜欢的电影,对F列降序排列，修改44页代码
top_female_ratings = mean_ratings.sort_values(by='F', ascending=False)
print(top_female_ratings[:5])
#
mean_ratings['diff'] = mean_ratings['M'] - mean_ratings['F']
sorted_by_diff = mean_ratings.sort_values(by='diff', ascending=False)
# print(sorted_by_diff[:5])
# print(sorted_by_diff[::-1][:5])