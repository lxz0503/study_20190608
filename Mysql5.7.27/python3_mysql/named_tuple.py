# coding=utf-8
from collections import namedtuple
import csv

def get_data(file_name):  # read data from csv file
    with open(file_name) as f:
        f_csv = csv.reader(f)
        headings = next(f_csv)  # use iterator
        # print(headings)  # ['name', 'status', 'arch', 'sprint']
        Row = namedtuple('Row', headings)  # this is a trick??? xiaozhan
        for r in f_csv:
            # print(r)   # 打印每行数据，但是不包括表头(因为前面用了next,所以已经走到了下一行),每行都是一个列表
            yield Row(*r)  # Row()的参数是一个可迭代对象

res = get_data('data.csv')
print(next(res))   # Row(name='ICMP-1.1', status=' Passed', arch=' IA', sprint=' sprint50')
# #
for i, t in enumerate(get_data('data.csv'), 1):  # the table index always starts from 1
    args = (i, t.name, t.status, t.arch, t.sprint)  # this is to generate parameter for excecutemany
    print(args)