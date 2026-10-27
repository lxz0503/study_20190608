# 过滤出1~100中平方根是整数的数：
# filter 是过滤原来的序列，返回执行结果为TRUE的元素组成新的序列
# !/usr/bin/python3
# -*- coding: UTF-8 -*-

import math


def is_sqr(x):
    return math.sqrt(x) % 1 == 0

# filter() 函数用于过滤序列，过滤掉不符合条件的元素，返回一个迭代器对象，如果要转换为列表，可以使用 list() 来转换。
# 该接收两个参数，第一个为函数，第二个为序列，序列的每个元素作为参数传递给函数进行判，然后返回 True 或 False，
# 最后将返回 True 的元素放到新列表中。
# 由于filter()函数的返回值是迭代器对象，所以需要使用list()函数将其转换为列表
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

