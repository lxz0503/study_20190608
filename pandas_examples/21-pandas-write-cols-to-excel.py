#!/usr/bin/env python3
# coding=utf-8
import pandas as pd
import re

def get_throughput(log):
    frame_data = []
    tcp_data = []
    udp_data = []
    pat = re.compile(r'iperf3.*-l\s(\d+)')
    with open(log, 'r') as f:
        for line in f:
            m = pat.search(line)
            if m is not None:
                frame_data.append(m.group(1))
            if re.search("receiver", line):
                tcp_data.append(line.split()[-3])
            if re.search('\d+%', line):
                udp_data.append(line.split()[-6])
        else:
            final_data = tcp_data + udp_data
    return list(map(int, final_data))  # 把字符串列表转化为整型列表


class PandasWriteExcel(object):
    def __init__(self, data, index):
        self.index = index
        self.data = data

    def write_to_excel(self):
        write_file = "test_cols.xlsx"
        df = pd.DataFrame(self.data, self.index)    # 用两个参数，dada里面已经包含了columns
        writer = pd.ExcelWriter(write_file)
        df.to_excel(writer, sheet_name='release', startrow=2, startcol=2)
        writer.save()


if __name__ == '__main__':
    index = ['tcp_64', 'tcp_1024', 'tcp_65536', 'udp_1400']
    data = {       # 数据里面已经包含了columns
        'SR0610': get_throughput('SR0610.txt'),
        'SR0620': get_throughput('SR0620.txt'),
        'SR0630': get_throughput('SR0630.txt'),
    }              # 每一列是一个release的全部数据

    ts = PandasWriteExcel(data, index)
    ts.write_to_excel()


