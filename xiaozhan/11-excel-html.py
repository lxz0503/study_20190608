# this can change one excel to a html
import pandas as pd
import codecs

def excel_to_html(filepath):
    xd = pd.ExcelFile(filepath)
    df = xd.parse()
    with codecs.open(r'F:\xiaozhan_git\study_20190608\xiaozhan\performance.html', 'w', 'utf-8') as html_file:
        html_file.write(df.to_html(header=True, index=False))
    file = open(r'F:\xiaozhan_git\study_20190608\xiaozhan\performance.html').read()
    return file

res = excel_to_html(r'F:\xiaozhan_git\study_20190608\xiaozhan\performance.xls')
print(res)