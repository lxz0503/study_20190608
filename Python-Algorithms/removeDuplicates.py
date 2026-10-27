#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/4/2022 2:13 PM
@file:removeDuplicates.py
@project:openpyxl_excel
"""
# 比较相邻元素，不需要从头到尾，只需要比较到len(set(iLst))即可，因为后面的iList[len(set(iList)):]必定是重复元素
from quickSort import quickSort

def removeDuplicates(iList):
    n = len(set(iList))    # 集合的去重特性，直接得出去重后的列表长度
    i = 0
    while i < n-1:   # 只需要比较到len(set(iLst))即可
        if iList[i] == iList[i+1]:
            temp = iList[i+1]   # 如果相邻数相同，把第二个存放到temp
            iList[i+1:len(iList)-1] = iList[i+2:]  # 将后面部分列表整体向前移动一位
            iList[-1] = temp    # 将相同元素的第二个排到列表尾部
        else:
            i += 1
    return iList[0:n]


if __name__ == "__main__":
    iList = [9, 3, 1, 2, 0, 8, 0]    # 也适用于有重复元素的排序
    print('before soring:', iList)
    iList = quickSort(iList)   # 先快速排序
    print('after sorting:', iList)
    print('after removing duplicates:', removeDuplicates(iList))

