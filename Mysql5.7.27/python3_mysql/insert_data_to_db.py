#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:11/8/2021 10:29 AM
@file:insert_data_to_db.py
@project:openpyxl_excel
"""
"""
This can read data from other file like txt or csv, and write data into mysql database.
It also supports other database functions like select,insert alter and update records.
"""
# !/usr/bin/python3
# coding=utf-8
import pymysql
from operations import *
import csv
from collections import namedtuple
import configparser


class DatabaseInit(object):
    def __init__(self):
        self.charset = 'utf8'
        self.host = '127.0.0.1'
        self.port = 3306
        self.db_name = 'test_result'
        self.username = 'root'
        self.password = '123win'
        self.conn = None
        self.cur = None

    def connect_db(self):                # this is to connect database system
        try:
            conn = pymysql.Connect(
                                   host=self.host,
                                   user=self.username,
                                   passwd=self.password,
                                   # db = self.dbname,    # this is only used when you already have a database
                                   charset=self.charset
                                  )
            cur = conn.cursor()
        except Exception as e:
            print("connect error", e)
        else:
            self.conn = conn
            self.cur = cur

    def disconnect_db(self):
        self.cur.close()
        self.conn.close()

    def create(self):           # this is for specific operations like creating database and table
        try:
            self.connect_db()
            self.cur.execute(drop_database)
            self.cur.execute(create_database)   # create database
            self.conn.select_db('test_result')  # connect your database
            # self.cur.execute(drop_table)
            self.cur.execute(create_table)      # create table
        except Exception as e:
            print("create error", e)
        else:
            self.conn.commit()    # do not forget to commit after modification
            self.disconnect_db()
            print('create database and table ok')

    @staticmethod
    def get_data(file_name):          # read data from csv file
        with open(file_name) as f:
            f_csv = csv.reader(f)
            headings = next(f_csv)    # use iterator
            Row = namedtuple('Row', headings)    # this is a trick??? xiaozhan
            for r in f_csv:
                yield Row(*r)     # r is a list

    def insert(self, insert_data, args):
        try:
            self.connect_db()
            self.cur.execute('use test_result')   # 里面可以直接写sql语句
            #
            # sql = "insert into students(name,age,gender,id) values(%s,%s,%s,%s)"
            # self.cur.execute(sql, ['zhangsan', 20, '男', 1])
            #
            self.cur.executemany(insert_data, args)   # this is ok,args是列表，可以防止sql注入
        except Exception as e:
            self.conn.rollback()
            print('insert error:', e)
        else:
            self.conn.commit()          # do not forget to commit after modification
            self.disconnect_db()


if __name__ == '__main__':
    db = DatabaseInit()      # 家里的win7只能用gbk编码,utf8 is for company
    db.connect_db()
    db.create()
    for i, t in enumerate(db.get_data('data.csv'), 1):      # set the table index always starts from 1
        args = [(t.name, t.status, t.arch, t.sprint)]      # this must be a list or tuple,dict，可以防止sql注入
        db.insert(insert_data, args)    # insert_data is at operations.py，











