#!/usr/bin/env python
# encoding=UTF-8

import xlrd
import os

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
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # file_path = root_dir + r'\data\test.xls'   # this is for windows
    file_path = root_dir + '/data/test.xls'    # this is for linux and mac
    print(file_path)           # F:\xiaozhan_git\study_20190608\Page_Object_UI_Test\data\test.xls
    readExcel(file_path, 1, 0)
    readExcels(file_path, 1, 0)
