#! /usr/bin/env python3
# coding=utf-8
# 给excel增加新的一列，并计算总分
import xlrd, xlwt

rbook = xlrd.open_workbook('demo.xls')
rsheet = rbook.sheet_by_index(0)

nc = rsheet.ncols   # 获取列数
rsheet.put_cell(0, nc, xlrd.XL_CELL_TEXT, '总分', None)   # 给原有的sheet增加新的一列

for row in range(1, rsheet.nrows):
    t = sum(rsheet.row_values(row, 1))   # 每行数据从第一列开始直到最后一列，相加
    rsheet.put_cell(row, nc, xlrd.XL_CELL_NUMBER, t, None)

# 把数据写入一个excel表
wbook = xlwt.Workbook()
wsheet = wbook.add_sheet(rsheet.name)  # 用来的sheet名字
style = xlwt.easyxf('align:vertical center, horizontal center')
# for循环从rsheet里面读取数据，同时写入另外一个表格
for r in range(rsheet.nrows):
    for c in range(rsheet.ncols):
        wsheet.write(r, c, rsheet.cell_value(r, c), style)

wbook.save('output_demo.xls')