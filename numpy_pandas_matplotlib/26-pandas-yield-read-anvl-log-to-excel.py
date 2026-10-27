"""
   Analyze test Logs one by one with regular expression.The original Logs is like:  << DHCP-SERVER-10.4: Passed
   Write test result into a txt file.
   And then read txt file and write result into excel with pandas
"""

# !/usr/bin/env python3
# coding=utf-8
import pandas as pd
import os
import re
import time


class PandasWriteExcel(object):
    def __init__(self):
        self.log_dir = os.path.dirname(__file__) + '/test_result'
        self.cur_time = self.get_time()

    def get_time(self):
        cur_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        return cur_time

    def gen_dir(self):     # generate Logs dir based on current time
        return os.makedirs(os.path.dirname(__file__) + '/report/' + self.cur_time + '/')

    def gen_file_name(self):     # generate Logs file based on the current time
        return self.cur_time + '.html'

    def get_logfile(self):
        for log_file in os.listdir(self.log_dir):
            yield log_file     # 迭代器每次处理一个log文件

    def gen_txt(self, name):    # 获取每行内容
        p = re.compile(r'<<.*-.*-\d+\.\d+: .*')      # this reg pattern is to match test result
        with open(self.log_dir + '/' + name) as f:  # process each Logs
            for line in f:           # analyze each test Logs
                r = p.match(line)
                if r is not None:
                    if r.group().__contains__('FAILED') or r.group().__contains__('INCONCLUSIVE'):
                        yield r.group().lstrip('<<').replace('!', '').replace(':', ',')  # 能够获取到每行的内容，例如 << DHCP-SERVER-10.4: Passed
                    else:   # 用,替代:是因为要暂时写入csv文件
                        yield r.group().lstrip('<<').replace(':', ',')

    def write_excel(self):
        # firstly, write every line into a csv file, because the pandas parameter must be file name
        with open("xiaozhan_test.csv", 'w') as fp:
            fp.write('Name,Result\n')     # add header
            log_names = self.get_logfile()   # 调用生成器函数,返回一个可迭代对象
            for name in log_names:         # analyze each test Logs
                lines = self.gen_txt(name)     # 调用生成器函数,返回一个可迭代对象----即每行的内容
                for line in lines:
                    fp.write(line + '\n')
        # read txt file and write into excel
        data = pd.read_csv('xiaozhan_test.csv', sep=',')
        data.sort_values(by='Name', inplace=True)  # sort by case name
        data.to_excel('test_result_rtnet.xlsx', sheet_name='anvl_result', index=False)

    def pd_read_excel(self):     # read data and store in a list as you like
        df = pd.read_excel('test_result.xlsx', header=None)  # 这个表示没有表头，即第一行就是数据,要设置header=None
        return df.values.tolist()


if __name__ == '__main__':
    t = PandasWriteExcel()
    t.write_excel()
    # print(t.gen_file_name())

# read data from another file and write it to excel
# data = pd.read_csv('test_result.Logs', sep=':')
# print(data.head())
# 把用冒号分割开的几列数据全部按列写到excel里面,大部分文本文件都可以用read_csv函数来处理
# data.to_excel('test_result.xlsx', sheet_name='result', index=False)