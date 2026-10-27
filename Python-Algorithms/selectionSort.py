#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:3/27/2022 1:08 PM
@file:selectionSort.py
@project:openpyxl_excel
"""
from randomList import randomList
import timeit

def selectionSort(iList):
    if len(iList) <= 1:
        return iList
    for i in range(0, len(iList)-1):
        if iList[i] != min(iList[i+1:]):  # 以开头基数和后面所有的数比较，min()函数直接找到了后面的最小值
            minIndex = iList.index(min(iList[i+1:]))   # minIndex is the index of the smallest number
            iList[i], iList[minIndex] = iList[minIndex], iList[i]   # change position
    return iList

if __name__ == "__main__":
    iList = randomList(10)
    # iList = [9,3,1,2,0,8,80]  # 不适用于有重复元素的排序
    print('before soring:', iList)
    print('after sorting:', selectionSort(iList))
    print('function time:', timeit.timeit(stmt="selectionSort", setup='from __main__ import selectionSort', number=1000000))

