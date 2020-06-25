"""
   Analyze test log one by one with regular expression.The original log is like:  << DHCP-SERVER-10.4: Passed
   Write test result into a txt file.
   And then read txt file and write result into excel with pandas
"""

# !/usr/bin/env python3
# coding=utf-8
import pandas as pd
import os
import re


class PandasWriteExcel(object):
    def __init__(self):
        self.log_dir = os.path.dirname(__file__) + '/test_result'

    def get_logfile(self):
        for log_file in os.listdir(self.log_dir):
            yield log_file     # 迭代器每次处理一个log文件

    def gen_txt(self, name):
        p = re.compile(r'<<.*-.*-\d+\.\d+: .*')      # this reg pattern is to match test result
        with open(self.log_dir + '/' + name) as f:
            for line in f:           # analyze each test log
                r = p.match(line)
                if r is not None:
                    yield r.group().lstrip('<<')

    def write_excel(self):
        # firstly, write every line into a file, because the pandas parameter must be file name
        with open("xiaozhan_test.txt", 'w') as fp:
            log_names = self.get_logfile()   # 调用生成器函数,返回一个可迭代对象
            for name in log_names:       # analyze each test log
                h = self.gen_txt(name)     # 调用生成器函数,返回一个可迭代对象
                for line in h:
                    fp.write(line + '\n')
        # read txt file and write into excel
        data = pd.read_csv('xiaozhan_test.txt', sep=':')
        data.to_excel('test_result.xlsx', sheet_name='anvl_result', index=False)


if __name__ == '__main__':
    t = PandasWriteExcel()
    t.write_excel()

# read data from another file and write it to excel
# data = pd.read_csv('test_result.log', sep=':')
# print(data.head())
# 把用冒号分割开的几列数据全部按列写到excel里面,大部分文本文件都可以用read_csv函数来处理
# data.to_excel('test_result.xlsx', sheet_name='result', index=False)