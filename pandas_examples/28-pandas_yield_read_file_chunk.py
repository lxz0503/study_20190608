#!/usr/bon/env python3
# coding=utf-8
# Panda read_csv()把第一行的数据变成了列名，怎么处理
# pandas DataFrame数据转为list
# 使用np.array()函数把DataFrame转化为np.ndarray()，再利用tolist()函数把np.ndarray()转为list
# this is to read a large file with pandas
# 每次读取5行

import pandas as pd

def pandas_read(filename, sep=',', size=5):
    # names参数可以决定列名,否则就会以第一列的名字默认作为列名,在这里可以去掉这个参数，只是作为提示
    reader = pd.read_csv(filename, sep, chunksize=size, header=None, names=['test result'])   # pd.dataframe
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
    print(type(next(g).values[0]))    # np.ndarray()   <class 'numpy.ndarray'>
    # print(next(g).values[0])
    print(np.array(next(g).values[0]).tolist())     # ['ICMP-4.4:Passed']   this is line 16 after 3 calls of next(g)
    print('case status is {}'.format(np.array(next(g).values[0]).tolist()[0].split(':')[1]))

