#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/13/2022 6:55 PM
@file:8-3-修改闭包内使用的外部函数的变量.py
@project:openpyxl_excel
"""
if __name__ == '__main__':
    # 函数嵌套
    def func_out():
        # 外部函数变量
        num1 = 10
        # 内部函数
        def func_inner(num):
            # 内部函数用了外部函数的变量
            # 闭包内修改外部函数的变量用nolocal
            nonlocal num1
            num1 = 20
            result = num1 + num
            print('result is:', result)
        # 外部函数返回值是内部函数
        return func_inner

    # 获取闭包,new_func就是闭包,  这个使用了外部函数变量的内部函数称为闭包
    new_func = func_out()
    # 执行闭包,   这个new_func实际上是和func_inner相关联，所以，如果添加参数，就直接在func_inner上添加即可
    new_func(1)  # 这个参数直接传给func_inner()
