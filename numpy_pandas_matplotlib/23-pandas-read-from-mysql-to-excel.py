#!/usr/bin/env python3
# coding=utf-8

import pymysql
import pandas as pd

# https://blog.csdn.net/qq_39192827/article/details/93990652    pandas 读取各种类型文件的例子

# create connection to database
conn = pymysql.Connect(host='127.0.0.1', user='root', passwd='123win', db='shop')
sql = 'select * from brand'   # prepare your sql command
# xiaozhan for str test
a = 'brand'
name = 'TCL'   # 注意下面的查询语句中 单引号和双引号
sql_t = 'select * from {} where name="{}"'.format(a,name)
print(sql_t)
t = pd.read_sql(sql_t, conn)
print(t.head(5))
# you can write data into csv
# t.to_csv('xiaozhan.csv', sep=',', index=False)    # this does not include index, like below:
# id,name,logo,describe,url,sort,cat_name,parent_cat_id,cat_id,is_hot
# 1,华为/HUAWEI,/Public/upload/brand/2016/04-01/1584936.jpg,1111111111,,50,手机、数码、配件,1,12,0
# 4,索尼/SONY,/Public/upload/brand/2016/04-01/4178854.jpg,,,50,手机、数码、配件,1,104,0

# write data into excel
# t.to_excel('from_sql.xlsx', sheet_name='anvl_result', index=False)