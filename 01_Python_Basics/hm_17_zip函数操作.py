"""
zip() 函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的列表。

如果各个迭代器的元素个数不一致，则返回列表长度与最短的对象相同，利用 * 号操作符，可以将元组解压为列表
在 Python 3.x 中为了减少内存，zip() 返回的是一个对象。如需展示列表，需手动 list() 转换。
"""
#!usr/bin/env python3
# coding=utf-8
a = [1, 2, 3]
b = ["xiaozhan", "beijing", "shanghai"]
c = [4, 5, 6, 7, 8]
zipped = zip(a, b)     # 打包为元组的列表
print("after zip and list", list(zipped))    # [(1, 'xiaozhan'), (2, 'beijing'), (3, 'shanghai')]
# 元素个数与最短的列表一致
l = [(1, 2), (3, 4), (5, 6)]
print(max(l))

a = [1, 2, 3]
b = [4, 5, 6]
c = [7, 8, 9]
d = [10, 11, 12]
zipped = zip(a, b, c, d)
print(list(zipped))      # [(1, 4, 7, 10), (2, 5, 8, 11), (3, 6, 9, 12)]
#
for i, m in enumerate(zip(a, b, c, d), start=1):
    print(i, ':',  m)

#  p = [[1,2,3],[4,5,6]]
# *字符称为解包运算符。当它出现在iterable对象后面时，它所做的就是将iterable中的项逐个传递给函数的调用方。
# 在本例中，由于zip函数接受一个iterable列表以返回其对齐列，zip(*p)将p中的所有项作为zip函数的参数传递：
#
# 因此，在这种情况下，zip(*p)等于：
#
# zip([1,2,3],[4,5,6])
