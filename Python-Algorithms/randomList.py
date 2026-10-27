#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:3/27/2022 11:24 AM
@file:randomList.py
@project:openpyxl_excel
"""
import random

def randomList(n):
    iList = []
    for i in range(n):
        iList.append(random.randrange(1000))  # 在大于0到小于1000的范围内，每次取一个数
    return iList


if __name__ == "__main__":
    iList = randomList(10)
    print(iList)
