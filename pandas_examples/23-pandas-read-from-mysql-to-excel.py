#!/usr/bin/env python3
# coding=utf-8

import pymysql
import pandas as pd

# create connection to database
conn = pymysql.Connect(host='127.0.0.1', user='root', passwd='123win', db='shop')
sql = 'select * from brand'   # prepare your sql command
t = pd.read_sql(sql, conn)
print(t.head(5))
# you can write data into csv
t.to_csv('xiaozhan.csv', sep=',', index=False)    # this does not include index, like below:
# id,name,logo,describe,url,sort,cat_name,parent_cat_id,cat_id,is_hot
# 1,华为/HUAWEI,/Public/upload/brand/2016/04-01/1584936.jpg,1111111111,,50,手机、数码、配件,1,12,0
# 4,索尼/SONY,/Public/upload/brand/2016/04-01/4178854.jpg,,,50,手机、数码、配件,1,104,0

# write data into excel
t.to_excel('from_sql.xlsx', sheet_name='anvl_result', index=False)