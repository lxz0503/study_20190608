#!/usr/bin/env python3
# coding=utf-8
# analyze data from test log and write into excel with pandas
import pandas as pd
import re


class PandasWriteExcel(object):
    def __init__(self, res_log, index, cols):
        self.res_log = res_log
        self.index = index
        self.cols = cols
        self.data = self.compose_data()

    # 正则表达式来解析日志，提取关键数据，存储到列表,列表元素必须是整型
    @staticmethod
    def get_throughput(log):
        tcp_data = []
        udp_data = []
        # pat = re.compile(r'iperf3.*-l\s(\d+)')
        with open(log, 'r') as f:
            for line in f:
                if re.search(r"receiver", line):
                    tcp_data.append(line.split()[-3])
                if re.search(r'\d+%', line):
                    udp_data.append(line.split()[-6])
            else:
                final_data = tcp_data + udp_data
        return list(map(int, final_data))  # change string into int type

    # 构造data frame的数据格式   compose data frame
    def compose_data(self):
        data = []
        for i in range(len(self.res_log)):  # 循环处理多个log文件  process multiple log files
            res = self.get_throughput(self.res_log[i])
            data.append(res)  # 每一个列表元素就是一个release的全部数据，即每一行 one list is one line
        return data  # [[247, 1082, 940, 6241], [247, 1082, 940, 6241], [247, 1082, 940, 6241]]

    # 将构造好的数据写到excel  write data frame to excel
    def write_to_excel(self):
        # write_file = "test.xlsx"  # you can use time to generate different excel name
        df = pd.DataFrame(self.data, self.index, self.cols)  # 三个参数

        df.to_excel('test.xlsx', sheet_name='release', startrow=0, startcol=0)


if __name__ == '__main__':
    index = ['SR0610', 'SR0620', 'SR0630']
    cols = ['tcp_64', 'tcp_1024', 'tcp_65536', 'udp_1400']
    res_log = ['SR0610.txt', 'SR0620.txt', 'SR0630.txt']
    # 实例化类对象  initialize class instance
    ts = PandasWriteExcel(res_log, index, cols)
    ts.write_to_excel()

# 在添加可迭代对象是，append在添加后不改变添加项的类型，添加之前是什么类型，添加之后就是什么类型；
# [1, 2, 3, 4, [5, 6, 7]]    [5,6,7]说就是用了append
# 而extend在添加后，会将添加项进行迭代，迭代的元素挨个添加到被添加的数组中：
# 再看下面的extend
# arr_ex = [1,2,3,4]
# item = [5,6,7]
# arr_ex.extend(item)
# [1, 2, 3, 4, 5, 6, 7]
