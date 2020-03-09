#!/usr/bin/env python3
# coding=utf-8
import pandas as pd
df = pd.DataFrame()
# url_list = ['http://www.espn.com/nba/salaries/_/seasontype/4']
url_list = ['http://www.espn.com/nba/salaries/_/page']
for i in range(2, 5):
    url = 'http://www.espn.com/nba/salaries/_/page/%s' % i
    url_list.append(url)

# 遍历网页中的table读取网页表格数据
for url in url_list:
    df = df.append(pd.read_html(url), ignore_index=True)
print(df.head(5))
# 列表解析：遍历dataframe第3列，以子字符串$开头,   ??????看不懂下面是处理什么
df = df[[x.startswith('$') for x in df[3]]]
print(df.head(3))
df.to_csv('NAB11.csv', header=['RK', 'NAME', 'TEAM', 'SALARY'], index=False)
