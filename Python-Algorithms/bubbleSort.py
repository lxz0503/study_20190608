#!/usr/bin/env python3
# coding=utf-8

from randomList import randomList
import timeit

def bubbleSort(iList):
    L = len(iList)
    for i in range(L):
        for n in range(1, L - i):
            if iList[n] < iList[n - 1]:   # if it is >,sort them in descending order
                iList[n - 1], iList[n] = iList[n], iList[n - 1]   # change position
    return iList

if __name__ == '__main__':
    iList = randomList(10)
    # iList = [9, 3, 1, 2, 0, 8, 0  # 也适用于有重复元素的排序
    print('before soring:', iList)
    print('after sorting:', bubbleSort(iList))
    print(timeit.timeit(stmt="bubbleSort", setup="from __main__ import bubbleSort", number=1000000))


