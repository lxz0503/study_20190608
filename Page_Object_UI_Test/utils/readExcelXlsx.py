#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 4/8/2021 3:21 PM
# @Email = lxz_20081025@163.com
# @Name = readExcelXlsx.py
from ParseExcel import ParseExcel
# 如果是测试用例的内容或者输入条件，经常每行存放一条数据
# 可以把每行数据放到一个字典，然后依次添加到一个列表里, 下面的代码可以实现此功能

def get_data(excel_file):
    pe = ParseExcel(excel_file)
    sheet = pe.get_sheet_by_name('test')  # test is the sheet name
    test_data = []
    for i in range(1, pe.get_rows_num(sheet) + 1):
        sub_data = {}
        sub_data['url'] = pe.get_each_row_values(sheet, i)[0]
        sub_data['data'] = pe.get_each_row_values(sheet, i)[1]
        sub_data['method'] = pe.get_each_row_values(sheet, i)[2]
        sub_data['expectation'] = pe.get_each_row_values(sheet, i)[3]
        test_data.append(sub_data)
    return test_data

if __name__ == '__main__':
    print('test data is\n')
    print(get_data('xiaozhan.xlsx'))
