# !/usr/bin/python
# coding:utf-8
import pymysql
import time

conn = pymysql.connect(host='localhost', user='root', password='123win')
pymysql.charset = 'gbk'
cur = conn.cursor()
conn.select_db('xiaozhan')
values = []
for i in range(10):
    value = (str(i), 'xiaxuan')
    values.append(value)
print(values)

now = time.strftime("%M:%S")
try:
    cur.executemany("insert into student values(%s,%s)", values)
    conn.commit()
except Exception as err:
    print(err)
finally:
    cur.close()
    conn.close()
end = time.strftime("%M:%S")


# 原文链接：https: // blog.csdn.net / u012734441 / article / details / 42269705