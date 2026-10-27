#!/usr/bin/env python3
# coding=utf-8

import openpyxl
from openpyxl import Workbook

wb = openpyxl.load_workbook('example.xlsx')
# ws = wb.worksheets
# # print(ws)
print(wb.get_sheet_names())     # this is a list
# ws.values是一个生成器
ws = wb.get_sheet_by_name('student')
print('type is {0}, values are {1}'.format(type(ws.values), ws.values))

# for i in ws.values:
#     print(type(i), i)

# openpyxl中提供了行列生成器（ws.rows和ws.columns），
# 这两个生成器里面存储了每一行（列）的数据，每一行由一个tuple包裹，便于对行列进行遍
for row in ws.rows:    # ws.rows也是一个生成器，用循环来读取
    print(*[cell.value for cell in row])

# create a new workbook  and write data
wb = Workbook()
ws = wb.active
print(ws)      # default is sheet
ws.title = 'student'
print(ws)        # now it is student
wb.create_sheet(index=0, title='new sheet')     # create a new sheet
ws = wb.active
# ws = wb.get_sheet_names()
print(ws)
ws['A1'] = 'hello'
ws['A2'] = 'beijing'
# wb.save('python-openpyxl.xlsx')    # save data into excel
