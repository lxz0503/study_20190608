#! /usr/bin/env python3
# coding=utf-8
# This can read data from one excel to a html
import pandas as pd
import codecs
import os

class ExcelToHtml(object):
    def __init__(self, excel_path, html_name):
        self.excel_path = excel_path
        self.html_name = html_name

    @property
    def excel_to_html(self):
        xd = pd.ExcelFile(self.excel_path)
        df = xd.parse()
        with codecs.open(self.html_name, 'w', 'utf-8') as html_file:
            html_file.write(df.to_html(header=True, index=False))
        # 下面的代码只是为了测试用
        with open(self.html_name) as f:
            res = f.read()
            if res is not None:
                return res


if __name__ == '__main__':
    excel_path = os.path.dirname(__file__) + '/test_data.xlsx'
    ts = ExcelToHtml(excel_path, 'test_data.html')
    print(ts.excel_to_html)
