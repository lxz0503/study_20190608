#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:3/27/2022 1:28 PM
@file:quickSort.py
@project:openpyxl_excel
"""
from randomList import randomList
import timeit

def quickSort(iList):
    if len(iList) <= 1:
        return iList
    left = []
    right = []
    for i in iList[1:]:   # 从第二个数开始，因为第一个数作为基准数
        if i <= iList[0]:    # iList[0]作为基准数
            left.append(i)
        else:
            right.append(i)
    return quickSort(left) + [iList[0]] + quickSort(right)


if __name__ == "__main__":
    # iList = randomList(10)   # 没有重复数据的排序
    iList = [9, 3, 1, 2, 0, 8, 0]    # 也适用于有重复元素的排序
    print('before soring:', iList)
    print('after soring:', quickSort(iList))
    print('quick sort time:', timeit.timeit(stmt="quickSort", setup="from __main__ import quickSort", number=1000000))
