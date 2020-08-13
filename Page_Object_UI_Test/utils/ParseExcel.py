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

    def get_rows_num(self, sheet):
        return sheet.max_row

    def get_cols_num(self, sheet):
        return sheet.max_column

    def get_start_row_num(self, sheet):
        return sheet.min_row

    def get_start_col_num(self, sheet):
        return sheet.min_column

    def get_row_values(self, sheet):
        # get values in all rows, a tuple,  this returns a generator
        try:
            return sheet.rows        # it is a generator
        except Exception as e:
            raise e

    def get_row_values_each(self, sheet, row):    # this can get values in specific row
        columns = self.get_cols_num(sheet)
        row_data = []
        for i in range(1, columns + 1):
            cell_value = sheet.cell(row=row, column=i).value
            row_data.append(cell_value)
        return row_data

    def get_col_values(self, sheet):
        # get values in all columns, a tuple
        try:
            return sheet.columns     # it is a generator for all columns
        except Exception as e:
            raise e

    def get_col_values_by_letter(self, sheet, col):    # just get one column like sheet['C']
        try:
            values = sheet[col]
            return [x.value for x in values if x.value is not None]    # return a list, you can define any format as you like
        except Exception as e:
            raise e

    def get_col_values_by_index(self, sheet, col):   # get value in specific column
        rows = self.get_rows_num(sheet)
        column_data = []
        for i in range(1, rows + 1):
            cell_value = sheet.cell(row=i, column=col).value
            column_data.append(cell_value)
        return column_data


    def get_cell_value(self, sheet, row_num, col_num):
        try:
            return sheet.cell(row=row_num, column=col_num).value
        except Exception as e:
            raise e

    def write_excel(self, sheet, row_num, col_num, content):
        try:
            sheet.cell(row=row_num, column=col_num).value = content
            self.workbook.save(self.excel_file)
        except Exception as e:
            raise e


if __name__ == '__main__':
    pe = ParseExcel()
    pe.load_workbook('xiaozhan.xlsx')
    sheet = pe.get_sheet_index(0)    # get sheet object
    # sheet = pe.get_sheet_name('test')
    print(sheet.title)    # the first sheet name
    # print(pe.get_cols_num(sheet))
    # get values in all rows and print each row
    r = pe.get_row_values(sheet)
    for row in r:
        for i in row:
            print(i.value, end=' ')
        print()    # this will help to split each row
    #
    # get values in all rows and print each row
    print('print value by column====================== as below')
    r = pe.get_col_values(sheet)
    for col in r:
        for i in col:
            print(i.value, end=' ')
        print()  # this will help to split each row

    # get values in specific line
    print(pe.get_row_values_each(sheet, 2))         # [1000, 2000, 3000, None]
    # get value in specific cell
    print(pe.get_cell_value(sheet, 3, 3))
    # write value into specific cell
    pe.write_excel(sheet, 4, 4, 'xiaozhan')
    # get values in column C
    print(pe.get_col_values_by_letter(sheet, 'C'))   # ['tianjin', 3000, 'dongcheng', None]

    # get values in column 1
    print(pe.get_col_values_by_index(sheet, 1))   # ['beijing', 1000, 'shunyi', None]



