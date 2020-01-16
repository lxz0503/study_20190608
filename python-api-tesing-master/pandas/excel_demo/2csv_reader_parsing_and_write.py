#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-19

import csv

input_file = r"supplier_data.csv"
output_file = r"output_files\2output.csv"
# 从一个csv文件里面读取数据，然后选取需要的，读取到另外一个csv文件里面

with open(input_file, 'r') as csv_in_file:
    with open(output_file, 'w') as csv_out_file:
        filereader = csv.reader(csv_in_file)
        filewriter = csv.writer(csv_out_file)
        for row_list in filereader:
            if row_list[1].startswith('001'):
            # 可以加一些判断条件，选取需要的数据写到文件里
                filewriter.writerow(row_list)