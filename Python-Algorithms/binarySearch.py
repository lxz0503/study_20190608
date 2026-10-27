#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/3/2022 9:19 PM
@file:binarySearch.py
@project:openpyxl_excel
"""
from randomList import randomList
from quickSort import quickSort
import random


def binarySearch(iList, key):
    print('iList=%s' % str(iList))
    print('Find the number %d' % key)
    iLen = len(iList)
    left = 0
    right = iLen - 1

    while right - left > 1:
        mid = (left + right) // 2   # 求商
        if key < iList[mid]:
            right = mid - 1
        elif key > iList[mid]:
            left = mid + 1
        else:   # 如果key刚好是中间那个数，返回下标
            return mid
    # 下面是上面的循环结束后，即只剩下两个元素了
    if key == iList[left]:
        return left
    elif key == iList[right]:
        return right
    else:   # 如果key不在这个列表中
        return -1

if __name__ == "__main__":
    # keys是一个列表，第一个元素在iList里，第二个元素不在
    iList = quickSort(randomList(20))
    keys = [random.choice(iList), random.randrange(min(iList), max(iList))]
    print(keys)
    for key in keys:
        res = binarySearch(iList, key)
        if res >= 0:
            print('%d is in the list,index is: %d\n' % (key,res))

        else:
            print('%d is not in the list\n' % key)
