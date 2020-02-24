#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-19

import csv

input_file = r"supplier_data.csv"
output_file = r"output_files\2output.csv"
# 从一个csv文件里面读取数据，然后选取需要的，读取到另外一个csv文件里面

with open(input_file, 'r') as csv_in_file:
    with open(output_file, 'w', newline='') as csv_out_file:       # newline='',换行符为空，默认为\n,看情况是否添加，一般设置为空，否则每两行之间有一空行
        f_reader = csv.reader(csv_in_file)    # 返回一个reader对象，利用该对象遍历csv文件中的行
        f_writer = csv.writer(csv_out_file)
        for row_list in f_reader:
            if row_list[1].startswith('001'):
            # 可以加一些判断条件，选取需要的数据写到文件里
                f_writer.writerow(row_list)