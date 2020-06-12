#!/usr/bin/env python3
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

plt.figure('pie', facecolor='lightgray')
plt.title('Pie')
labels = ['python', 'C', 'C++', 'JS', 'PHP', 'JAVA']
sizes = [2, 5, 12, 70, 2, 9]
explode = (0.1, 0, 0, 0.1, 0, 0)   # 0.1表示把那部分从饼图里拿出来
plt.pie(sizes, labels=labels, explode=explode, autopct='%1.1f%%', shadow=False, startangle=150)
# plt.savefig('pie.jpg')
plt.show()