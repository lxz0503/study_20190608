import matplotlib.pyplot as plt
import xlrd
from xlrd import open_workbook
import os

x_data = []
y_data = []
x_volte = []
temp = []
f_dir = os.path.dirname(__file__) + '/pandas_examples.xls'
wb = open_workbook(f_dir)
for s in wb.sheets():
    # print('Sheet:', s.name)
    for row in range(s.nrows):
        # print('the row is:', row)
        values = []
        for col in range(s.ncols):
            values.append(s.cell(row, col).value)
        print(values)   # 每一行的数据存储在一个列表里 ['beijing', 1000.0]
        x_data.append(values[0])
        y_data.append(values[1])
print(x_data)  # the first column
print(y_data)  # the second column
plt.plot(x_data, y_data, 'bo-', label=u"Phase curve", linewidth=1)
plt.title(u"TR14 phase detector")
plt.legend()

plt.xlabel(u"input-deg")
plt.ylabel(u"output-V")

plt.show()
#plt.savefig(r"D:\xiaozhan_git\study_20190608\pandas_examples\line.jpg")  # 保存图
