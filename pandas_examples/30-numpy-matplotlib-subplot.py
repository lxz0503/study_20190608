#!/usr/bin/env python3
# coding=utf-8
# 两行三列，总共6个数字，分别放在一个图片里
from matplotlib import pyplot as plt

plt.figure(facecolor='lightgray')
for i in range(2):
    for j in range(3):
        k = i * 3 + j + 1
        plt.subplot(2, 3, k)
        plt.xticks(())
        plt.yticks(())
        # plt.title('xiaozhan')
        plt.text(0.5, 0.5, str(k), ha='center', va='center', size=36, alpha=0.5)
plt.tight_layout()
plt.show()


