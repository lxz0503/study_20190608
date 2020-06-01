#!/usr/bin/env python3
# coding=utf-8
from contextlib import contextmanager
import pymysql
import csv
from collections import namedtuple

@contextmanager
def get_conn(**kwargs):
    conn = pymysql.connect(host=kwargs.get('host','localhost'),
                      user=kwargs.get('user'),
                      passwd=kwargs.get('passwd'),
                      charset=kwargs.get('charset'))
    try:
        yield conn
    finally:
        if conn:
            conn.close()


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
            conn.select_db('xiaozhan')
            cur.execute(sql)
        except:
            # 发生错误时回滚
            pass

def main():
    conn_args = dict(host='localhost', user='root', password='123win', charset="utf8")
    with get_conn(**conn_args) as conn:
        SQL_FORMAT = """insert into student values({0}, {1}, {2})"""
        for t in get_data('data.csv'):
            sql = SQL_FORMAT.format(t.index, t.name, t.status)
            execute_sql(conn, sql)

if __name__ == '__main__':
    main()

