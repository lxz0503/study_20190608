#! /user/bin/env python3
# coding=utf-8
# 如果有中文字符，注意设置pycharm软件的编码为UTF-8即可,并设置文件编码为UTF-8

import pandas as pd
import os
import codecs

f_dir = os.path.dirname(__file__) + '/taobao_data.csv'
# df = pd.read_csv(f_dir, delimiter=',', encoding='gb2312', header=0)
df = pd.read_csv(f_dir, delimiter=',', encoding='utf-8', header=0)
print(df)

# 向csv写入数据
df.to_csv('taobao_price_data_xiaozhan.csv', columns=['商品', '价格'], index=True, header=True)

