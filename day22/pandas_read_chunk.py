#!/usr/bon/env python3
# coding=utf-8
# Panda read_csv()把第一行的数据变成了列名，怎么处理
# this is to read a large file with pandas
# 每次读取5行

import pandas as pd

def pandas_read(filename, sep=',', size=5):
    # names参数可以决定列名,否则就会以第一列的名字默认作为列名
    reader = pd.read_csv(filename, sep, chunksize=size, header=None, names=['test result'])
    while True:
        try:
            yield reader.get_chunk()
        except StopIteration:
            print('Done')
            break


if __name__ == '__main__':
    g = pandas_read('test_result.log', sep='\n')
    # for c in g:
    #     print(c)
    print('case name is {}'.format((next(g).values[0][0].split(':')[0])))
    print('case status is {}'.format((next(g).values[0][0].split(':')[1])))
    print(type(next(g).values[0]))
    print(next(g).values[0])
