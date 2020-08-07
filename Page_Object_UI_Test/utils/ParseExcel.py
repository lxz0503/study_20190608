"""Operate excel file."""
# !/usr/bin/env python3
# coding=utf-8
import time
import openpyxl
from openpyxl.styles import Border, Side, Font

class ParseExcel(object):
    def __init__(self):
        self.workbook = None
        self.excel_file = None
        self.font = Font(color=None)
        self.RGBDict = {'red': 'FFFF3030', 'green': 'FF008B00'}

    def load_workbook(self, excel_path_name):
        try:
            self.workbook = openpyxl.load_workbook(excel_path_name)
        except Exception as e:
            raise e
        self.excel_file = excel_path_name
        return self.workbook

    def get_sheet_name(self, sheet_name):    # get sheet object
        try:
            sheet = self.workbook[sheet_name]
            return sheet
        except Exception as e:
            raise e

    def get_sheet_index(self, sheet_index):   # get sheet by index
        try:
            sheet_name = self.workbook.sheetnames[sheet_index]
        except Exception as e:
            raise e
        sheet = self.workbook[sheet_name]
        return sheet

    def get_rows_number(self, sheet):
        return sheet.max_row

    def get_cols_number(self, sheet):
        return sheet.max_column


if __name__ == '__main__':
    pe = ParseExcel()
    pe.load_workbook('xiaozhan.xlsx')
    sheet = pe.get_sheet_index(0)    # get sheet object
    # print(pe.get_sheet_name('test').title)
    print(pe.get_sheet_index(0).title)    # the first sheet name
    print(pe.get_rows_number(sheet))


