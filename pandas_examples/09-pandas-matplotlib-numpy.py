from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

x = np.arange(0., 10, 0.2)
y1 = np.cos(x)
y2 = np.sin(x)
y3 = np.sqrt(x)
# show the legend
plt.grid(True)   # 也可不不设置网格线
plt.plot(x, y1, color='blue', linewidth=1.5, linestyle='-', marker='.', label="y=cos(x)")
plt.plot(x, y2, color='green', linewidth=1.5, linestyle='-', marker='*', label="y=sin(x)")
plt.legend(loc='upper right')   # 关键，设置图例
# plt.savefig(r"D:\xiaozhan_git\study_20190608\pandas_examples\test1.jpg")
plt.show()

# subplot

plt.figure(figsize=(6, 4))

# plt.subplot(n_rows, n_cols, plot_num)

plt.subplot(2, 2, 1)

plt.plot([0, 1], [0, 1])

plt.subplot(222)

plt.plot([0, 1], [0, 2])

plt.subplot(223)

plt.plot([0, 1], [0, 3])

plt.subplot(224)

plt.plot([0, 1], [0, 4])

plt.tight_layout()
plt.show()

# ---------------------
# 作者：changzoe
# 来源：CSDN
# 原文：https://blog.csdn.net/changzoe/article/details/78845756
# 版权声明：本文为博主原创文章，转载请附上博文链接！