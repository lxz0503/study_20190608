#!/usr/bin/env python
# encoding=UTF-8

import xlrd

def readExcel(file, row, sheet_id):
    book = xlrd.open_workbook(file, 'r')
    sheet = book.sheet_by_index(sheet_id)
    print(sheet.row_values(row))
    return sheet.row_values(row)

def readExcels(file, row, sheet_id):
    rows = []
    book = xlrd.open_workbook(file, 'r')
    sheet = book.sheet_by_index(sheet_id)
    for row in range(1, sheet.nrows):
        rows.append(sheet.row_values(row, 0, sheet.ncols))
    print(rows)
    return rows

if __name__ == "__main__":
    readExcel(r'D:\xiaozhan_git\study_20190608\UI\data\test.xls', 1, 0)
    readExcels(r'D:\xiaozhan_git\study_20190608\UI\data\test.xls', 1, 0)
