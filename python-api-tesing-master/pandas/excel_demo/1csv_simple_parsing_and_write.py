#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-19

# 从一个csv文件读取内容到另外一个csv文件
input_file = r"supplier_data.csv"
output_file = r"output_files\1output.csv"

with open(input_file, 'r') as f_reader:
    with open(output_file, 'w') as f_writer:
        for row in f_reader:
            f_writer.write(row)