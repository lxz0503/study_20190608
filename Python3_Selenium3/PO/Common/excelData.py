import xlrd, os
import pandas as pd


# 读excel操作、所有数据存放字典中
# filename为文件名
# index为excel sheet工作簿索引
def read_excel(filename, index):
    xls = xlrd.open_workbook(filename)
    sheet = xls.sheet_by_index(index)
    print(sheet.nrows)
    print(sheet.ncols)
    dic = {}
    for j in range(sheet.ncols):
        data = []
        for i in range(sheet.nrows):
            data.append(sheet.row_values(i)[j])
        dic[j] = data
    return dic

def pd_read_excel(filename, sheet_name):
    df = pd.read_excel(filename, 'xiaozhan', header=None, skiprows=1)
    test_data = []
    for i in df.index.values:  # 获取行号的索引，并对其进行遍历：
        # 根据i来获取每一行指定的数据 并利用to_list转化成列表
        row_data = df.iloc[i, :].to_list()  # this is for pandas v1.0,把每行数据读到一个列表里，默认不包含表头，即第一行
        # print(row_data)
        test_data.append(row_data)
    return test_data


if __name__ == '__main__':
    # 读取excel操作，返回字典
    # data = read_excel(os.path.split(os.path.realpath(__file__))[0].split('C')[0] + "Data\\testdata.xlsx", 0)
    # print(data)
    # print(data.get(1))
    # read data with pandas
    filename = os.path.split(os.path.realpath(__file__))[0].split('C')[0] + "Data\\testdata.xlsx"
    sheet_name = 'xiaozhan'
    pd_read_excel(filename, sheet_name)
