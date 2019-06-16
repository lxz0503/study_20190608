# this is for drawing pictures with python
import numpy as np
import matplotlib.pyplot as plt

x = [0, 1]
y = [0, 1]
plt.figure()
plt.plot(x, y)
plt.xlabel("time(s)")
plt.ylabel("value(m)")
plt.title("A simple plot")
plt.show()
plt.savefig(r"D:\Pycharm\文本处理\easyplot.jpg")

#
x = [0,1,2,3,4,5,6]
y = [0.3,0.4,2,5,3,4.5,4]
plt.figure(figsize=(8,4))  # 创建绘图对象
plt.plot(x,y,"b--",linewidth=1)    # 在当前绘图对象绘图（X轴，Y轴，蓝色虚线，线宽度）
plt.xlabel("Time(s)")  # X轴标签
plt.ylabel("Volt")   # Y轴标签
plt.title("Line plot")  # 图标题
# plt.show()  # 显示图,如果显示出来，就不会保存在本地
plt.savefig(r"D:\Pycharm\文本处理\line.jpg")  # 保存图

# 作者：YanniZhang的博客
# 来源：CSDN
# 原文：https://blog.csdn.net/jenyzhang/article/details/52046372
# 版权声明：本文为博主原创文章，转载请附上博文链接！