"""
获取表格中的最高和最低温度并画图
"""
import csv
from matplotlib import pyplot as plt
from datetime import datetime
import os

# 读取CSV文件数据
filename = r'D:\xiaozhan_git\study_20190608\xiaozhan\sitka_weather_2014.csv'
with open(filename) as f:  # 打开这个文件，并将结果文件对象存储在f中
    reader = csv.reader(f)  # 创建一个阅读器reader
    next(reader)  # 返回文件中的下一行,第一行不是数据，所以直接跳过去
    dates, highs, lows = [], [], []  # 声明存储日期，最值的列表
    for row in reader:
        current_date = datetime.strptime(row[0], '%Y-%m-%d')  # 将日期数据转换为datetime对象
        dates.append(current_date)  # 存储日期
        high = int(row[1])  # 将字符串转换为数字
        highs.append(high)  # 存储温度最大值
        low = int(row[3])
        lows.append(low)  # 存储温度最小值

# 根据数据绘制图形
fig = plt.figure(dpi=128, figsize=(10, 6))
plt.plot(dates, highs, c='red', alpha=0.5)  # 实参alpha指定颜色的透明度，0表示完全透明，1（默认值）完全不透明
plt.plot(dates, lows, c='blue', alpha=0.5)
plt.fill_between(dates, highs, lows, facecolor='blue', alpha=0.1)  # 给图表区域填充颜色
plt.title('Daily high and low temperature-2004', fontsize=24)
plt.xlabel('', fontsize=16)
plt.ylabel('Temperature(F)', fontsize=16)
plt.tick_params(axis='both', which='major', labelsize=16)
fig.autofmt_xdate()  # 绘制斜的日期标签
jpg_dir = os.path.dirname(__file__) + '/csv1.jpg'
plt.savefig(jpg_dir)
plt.show()
# ---------------------
# 作者：Asia - Lee
# 来源：CSDN
# 原文：https: // blog.csdn.net / asialee_bird / article / details / 79589307
# 版权声明：本文为博主原创文章，转载请附上博文链接！