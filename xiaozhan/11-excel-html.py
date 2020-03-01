# this can change one excel to a html
import pandas as pd
import codecs
import os


def excel_to_html(excel_path, html_name):
    xd = pd.ExcelFile(excel_path)
    df = xd.parse()
    with codecs.open(html_name, 'w', 'utf-8') as html_file:
        html_file.write(df.to_html(header=True, index=False))
    # debug
    # file = open(html_name).read()
    # return file


if __name__ == '__main__':
    excel_path = os.path.dirname(__file__) + '/test_data.xlsx'
    excel_to_html(excel_path, 'test_data.html')
