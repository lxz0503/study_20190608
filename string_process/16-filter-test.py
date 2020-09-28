# 过滤出1~100中平方根是整数的数：
# filter 是过滤原来的序列，返回执行结果为TRUE的元素组成新的序列
# !/usr/bin/python3
# -*- coding: UTF-8 -*-

import math


def is_sqr(x):
    return math.sqrt(x) % 1 == 0


newlist = filter(is_sqr, range(1, 101))
print(list(newlist))
# TODO:use comprehension,列表表达式
res = [x for x in range(1, 101) if math.sqrt(x) % 1 == 0]
print(res)
# TODO: use a function
def is_odd(n):
    return n % 2 == 1


newlist = filter(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print(list(newlist))
# TODO:use列表表达式， comprehension
res = [x for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] if x % 2 == 1]
print(res)

