#!/usr/bin/env python3
# coding=utf-8
import pandas as pd
import re


class PandasWriteExcel(object):
    def __init__(self, res_log, index, cols):
        self.res_log = res_log
        self.index = index
        self.cols = cols
        self.data = self.compose_data()

    @staticmethod
    def get_throughput(log):
        # frame_data = []
        tcp_data = []
        udp_data = []
        # pat = re.compile(r'iperf3.*-l\s(\d+)')
        with open(log, 'r') as f:
            for line in f:
                # m = pat.search(line)
                # if m is not None:
                #     frame_data.append(m.group(1))
                if re.search(r'receiver', line):
                    tcp_data.append(line.split()[-3])
                if re.search(r'\d+%', line):
                    udp_data.append(line.split()[-6])
            else:
                final_data = tcp_data + udp_data
        return list(map(float, final_data))  # 把字符串列表转化为整型列表# 构造dataframe的数据格式

    def compose_data(self):
        data = []
        for i in range(len(self.res_log)):
            res = self.get_throughput(self.res_log[i])
            data.append(res)  # 每一个列表元素就是一个release的全部数据，即每一行
        # print(f'performance result:{data}')      # [[247, 1082, 940, 6241], [247, 1082, 940, 6241]]
        return dict(zip(self.cols, data))     # 返回一个字典，组成dataframe的数据格式

    def write_to_excel(self):
        write_file = "test_cols.xlsx"
        df = pd.DataFrame(self.data, self.index)  # 两个参数
        writer = pd.ExcelWriter(write_file)
        df.to_excel(writer, sheet_name='release', startrow=2, startcol=2)
        writer.save()


if __name__ == '__main__':
    # 和上一个例子的区别就是index和column的名字不同，需求不同
    index = ['tcp_64', 'tcp_1024', 'tcp_65536', 'udp_1400']
    cols = ['SR0610', 'SR0620', 'SR0630']
    res_log = ['SR0610.txt', 'SR0620.txt', 'SR0630.txt']           # 每一列是一个release的全部数据
    # 实例化类对象
    ts = PandasWriteExcel(res_log, index, cols)
    ts.write_to_excel()


