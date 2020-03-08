#!/usr/bin/env python3
# coding=utf-8
# https://www.cnblogs.com/apollo1616/articles/9785335.html

# reduce函数，reduce函数会对参数序列中元素进行累积。
# reduce函数的定义：
# reduce(function, sequence [, initial] ) -> value
# function参数是一个有两个参数的函数，reduce依次从sequence中取一个元素，和上一次调用function的结果做参数再次调用function。
# 第一次调用function时，如果提供initial参数，会以sequence中的第一个元素和initial作为参数调用function，否则会以序列sequence中的前两个元素做参数调用function。

# 对列表求和
from functools import reduce
lst = [1, 2, 3, 4]
print(reduce(lambda x, y: x+y, lst))
#
lst=[1,2,3,4]
print(reduce(lambda x, y: x*y, lst))

#
print(reduce(lambda x, y: x*y+1, lst))

#计算过程如下:
# 这个式子只有两个参数,没有初始化值,那么就取列表前2项,通过lambda函数计算结果
#1*2+1=3,
#上面计算的结果在与列表第三个元素通过lambda函数计算
# 3*3+1=10
#上面计算的结果在与列表第四个元素通过lambda函数计算
# 10*4+1=41

# 有初始化值的情况, 这个时候就不是取列表的前两项, 而是取初始值为第一个,序列的第一个元素为第二个元素,开始进行lambda函数的应用计算.
lst=[1,2,3,4]
print(reduce(lambda x,y: x+y, lst,5))

# 5是初始值,也可以理解为第三个参数
# 计算呢过程
# -->5+1=6
# -->6+2=8
# -->8+3=11
# -->11+4=15