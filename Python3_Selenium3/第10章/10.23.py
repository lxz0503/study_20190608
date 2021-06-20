def read_excel(filename, index, cloumn):
#表明运用xlrd模块的open方法来打开Excel文件
xls = xlrd.open_workbook(filename)
#表明要选择的表格
sheet = xls.sheet_by_index(index)
#打印选定表格的行数
print(sheet.nrows)
#打印选定表格的列数
print(sheet.ncols)
#声明一个空的列表data
data = []
#表明用for循环遍历Excel中的第一列的数据然后将遍历加入到列表data中
    for i in range(sheet.nrows):
        data.append(sheet.row_values(i)[0])
        print(sheet.row_values(i)[0])
    #返回列表data
    return data	
