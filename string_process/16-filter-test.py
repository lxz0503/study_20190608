# 过滤出1~100中平方根是整数的数：
# !/usr/bin/python3
# -*- coding: UTF-8 -*-

import math


def is_sqr(x):
    return math.sqrt(x) % 1 == 0


newlist = filter(is_sqr, range(1, 101))
print(list(newlist))


def is_odd(n):
    return n % 2 == 1


newlist = filter(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print(list(newlist))

