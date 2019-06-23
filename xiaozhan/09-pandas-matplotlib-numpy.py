from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

x = np.arange(0., 10, 0.2)
y1 = np.cos(x)
y2 = np.sin(x)
y3 = np.sqrt(x)
# show the legend
plt.plot(x, y1, color='blue', linewidth=1.5, linestyle='-', marker='.', label="y=cos(x)")
plt.plot(x, y2, color='green', linewidth=1.5, linestyle='-', marker='*', label="y=sin(x)")
plt.legend(loc='upper right')   # 关键，设置图例
# plt.savefig(r"D:\xiaozhan_git\study_20190608\xiaozhan\test1.jpg")
plt.show()