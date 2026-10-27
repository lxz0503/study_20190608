#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/14/2022 7:54 PM
@file:8-5-装饰器使用-统计函数执行时间.py
@project:openpyxl_excel
"""
# http://c.biancheng.net/view/2270.html       refer to this link
# 装饰器本身就是一个闭包函数，不会修改被修饰函数里面的代码，不能修改函数的调用方式。这是原则
# 可以理解为在一个函数外面加另外一个函数，来实现某些功能
# 应用场景，例如, 不能修改函数体
# 装饰器 = 高阶函数 + 函数嵌套 + 闭包
import time


def deco(func):  # 有且只有一个参数，以函数名作为参数,就是高阶函数  high level function
    def wrapper(a, b):  # 函数嵌套       function nesting
        start_time = time.time()
        func(a, b)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        print("time is %d ms" % execution_time)

    return wrapper  # 返回值是嵌套函数的函数名


@deco
def f(a, b):
    print("be on")
    time.sleep(1)
    print("result is %d" % (a + b))  # 执行完这一步，跳转到def wrapper(a,b)里面的f(a,b)


if __name__ == '__main__':
    f(3, 4)  # 此处设置断点，查看函数如何执行,顺序是先执行deco()函数，跳到19行，然
    # 后20行，再地28行，29行，执行完30行，31  32
    # 再回到def wrapper(a,b)里面的func(a,b)，再第21行，22，23行,再返回到36行，函数执行结束
