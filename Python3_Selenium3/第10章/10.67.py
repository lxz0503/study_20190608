#coding=utf-8
import  xlrd

# excel值封装，返回就是一个字典
#参数命名需要修改下
# demo数据返回[{'username': 'tim1', 'passwd': 'TimTest'}, {'username': 'tim2', 'passwd': 'TimTest'}, {'username': 'tim3', 'passwd': 'TimTest'}]

def get_data(filename, sheetnum):
    path = 'testdata.xlsx'
    book_data = xlrd.open_workbook(path)
    book_sheet = book_data.sheet_by_index(1)  # 打开文件的中第一个表
    rows_num = book_sheet.nrows  # 行数
    rows0 = book_sheet.row_values(0)  # 第一行的各个名称作为字典的键
    rows0_num = len(rows0)  # 这个可以知道有几列
    list = []

    for i in range(1, rows_num):
        rows_data = book_sheet.row_values(i)  # 取每一行的值作为列表
        rows_dir = {}
        for y in range(0, rows0_num):  # 将每一列的值与每一行对应起来
            rows_dir[rows0[y]] = rows_data[y]
        list.append(rows_dir)
    return list


if __name__ == '__main__':
    print(get_data('', 1))
