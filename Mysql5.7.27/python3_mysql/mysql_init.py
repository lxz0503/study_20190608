#!/usr/bin/python3
import pymysql
import time
from python3_mysql.operations import *

class DatabaseInit(object):
    def __init__(self, host, dbname, username, password, charset):
        self.host = host
        self.dbname = dbname
        self.username = username
        self.password = password
        self.charset = charset
        self.conn = None
        self.cur = None

    def connect_db(self):
        try:
            conn = pymysql.Connect(
                                   host=self.host,
                                   user=self.username,
                                   passwd=self.password,
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

    def create(self):
        try:
            self.connect_db()
            self.cur.execute(drop_database)
            self.cur.execute(create_database)
            self.conn.select_db('test_result')
            # self.cur.execute(drop_table)
            self.cur.execute(create_table)
        except Exception as e:

            print("create error", e)
        else:
            self.conn.commit()    # do not forget to commit after modification
            self.disconnect_db()
            print('create database and table ok')

    def insert_data(self, insert_data, args):
        try:
            self.connect_db()
            self.cur.execute('use test_result')
            # self.conn.select_db('test_result')
            # self.cur.execute(insert_data)
            self.cur.executemany(insert_data, args)
        except Exception as e:
            self.conn.rollback()
            print('insert error:', e)
        else:
            self.conn.commit()          # do not forget to commit after modification
            self.disconnect_db()

    def search_data(self):
        try:
            self.connect_db()
            self.cur.execute('use test_result')
            self.cur.execute('select * from ia_result')
            res = self.cur.fetchall()
        except Exception as e:
            print(e)
        else:
            self.disconnect_db()
            # print('Failed cases are:')
            fail_dict = {}
            for row in res:
                if row[2] == 'FAIL':
                    fail_dict.setdefault(row[1], row[2])
            return fail_dict

    def update_data(self):
        try:
            self.connect_db()
            self.cur.execute('use test_result')
            self.cur.execute(update_data)
        except Exception as e:
            self.conn.rollback()
            print('update error:', e)
        else:
            self.conn.commit()    # do not forget to commit after modification
            self.disconnect_db()

    def alter_table(self):
        try:
            self.connect_db()
            self.cur.execute('use test_result')
            self.cur.execute(alter_table)
        except Exception as e:
            self.conn.rollback()
            print('alter error:', e)
        else:
            self.conn.commit()    # do not forget to commit after modification
            self.disconnect_db()

if __name__ == '__main__':
    db = DatabaseInit(host='localhost',
                      dbname='test_result',
                      username='root',
                      password='123win',
                      charset='gbk')      # 家里的win7只能用gbk编码
    db.connect_db()
    db.create()
    db.insert_data(insert_data, args)
    db.search_data()
    # this can put failed cases into a dictionary
    res = db.search_data()
    print(res)
    # after rerun, you need to update test result again
    db.alter_table()   # add date column
    db.update_data()
    time.sleep(5)
    res = db.search_data()  # tuple change to a list
    if len(res) != 0:
        print('modify not ok, check log')









