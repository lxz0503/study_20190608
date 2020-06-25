#!/usr/bin/env python3
# coding=utf-8
import pandas as pd
from openpyxl import load_workbook

df = pd.read_excel('bug_copy.xlsx')
book = load_workbook('bug_copy.xlsx')
#
writer = pd.ExcelWriter('bug_copy.xlsx', engine='openpyxl')
writer.book = book
# get all sheets
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
df['Add'] = [10, 20, 30, 40, 50, 60]
# write data
df.to_excel(writer, sheet_name='Sheet2', index=0, startrow=0, startcol=0)
writer.save()


