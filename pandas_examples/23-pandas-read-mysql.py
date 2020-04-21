#!/usr/bin/env python3
# coding=utf-8

import pymysql
import pandas as pd

conn = pymysql.Connect(host='127.0.0.1', user='root', passwd='123win', db='shop')
sql = 'select * from brand'
t = pd.read_sql(sql, conn)
print(t)
