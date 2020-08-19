#!/usr/bin/env python3
# coding=utf-8
l = sum(i for i in range(10))  # 用小括号就是生成器
print(l)

l = sum([i for i in range(10)])  # 列表生成式
print(l)

# 文件中最长的那一行的长度，去掉空格

res = max(len(x.strip()) for x in open("population_statistics"))
print('the max len is %s' % res)

# 如果列表内容特别大，就用生成器表达式，把[]替换为()即可,这样不会真用很大内存

l = (i for i in range(10))
print(l)  # <generator object <genexpr> at 0x000000000213F780>
print(l.__next__())   # 这里输出0
print(l.__next__())   # 这里输出1

# yield相当于函数里面的return
#
# def test():
#     print("first")
#     yield "the first"
#     print("second")
#     yield 2
#     print("third")
#     yield 3
# res = test()
# print(res.__next__())   # 这里输出1
# print(res.__next__())   # 这里输出2
