# !/usr/bin/python
# coding:utf-8
import pymysql
import time
import csv
from collections import namedtuple

def get_data(file_name):
    with open(file_name) as f:
        f_csv = csv.reader(f)
        headings = next(f_csv)
        Row = namedtuple('Row', headings)
        for r in f_csv:
            yield Row(*r)


def execute_sql(conn, sql):
    with conn as cur:
        try:
            cur.execute(sql)
        except:
            # 发生错误时回滚
            pass


conn = pymysql.connect(host='localhost', user='root', password='123win')
pymysql.charset = 'utf8'
cur = conn.cursor()
conn.select_db('xiaozhan')

SQL_FORMAT = """insert into `student` values ({0}, '{1}', '{2}')"""
for t in get_data('data.csv'):
    sql = SQL_FORMAT.format(t.index, t.name, t.status)
    print(sql)
    cur.execute(sql)
    # execute_sql(conn, sql)
# try:
#     cur.execute(conn, sql)
#     conn.commit()
# except Exception as err:
#     print(err)
#     conn.rollback()
# finally:
#     cur.close()
#     conn.close()


# 原文链接：https: // blog.csdn.net / u012734441 / article / details / 42269705