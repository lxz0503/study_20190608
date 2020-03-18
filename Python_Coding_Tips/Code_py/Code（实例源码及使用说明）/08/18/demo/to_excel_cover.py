#!/usr/bin/env python3
# coding=utf-8
# https://www.cnblogs.com/wanglle/p/11455758.html   this is old method without pandas
# 向一个现有的excel中写入新的数据，不覆盖原来的sheet
# 如果不用下面的方法，会默认覆盖原有的sheet，然后默认把数据写入指定的sheet，其他原有sheet全部清零

import pandas                          # 导入pandas模块
from openpyxl import load_workbook     # 导入excel操作模块

df = pandas.read_excel('demo.xlsx')   # 读取excel文件
book = load_workbook('demo.xlsx')     # 加载文件
# 创建写入对象
writer = pandas.ExcelWriter('demo.xlsx', engine='openpyxl')
writer.book = book
# 获取所有sheet
for ws in book.worksheets:
    print(type(ws),'---',ws)
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
print(writer.sheets)
df['Add'] = [10, 20, 30, 40, 50]      # 添加Add列数据
# 写入数据
# df.to_excel(writer, "Sheet1", index=0, startrow=0, startcol=0)
# writer.save()             # 保存
