#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/2/2022 4:31 PM
@file:34_lambda_func.py
@project:openpyxl_excel
"""
# https://zhuanlan.zhihu.com/p/134024110
# 创建 lambda 函数的语法为：
# lambda [parameters]: expression

if __name__ == "__main__":
    # 可变参数
    fn1 = lambda *args: args
    print(fn1(10,20,30))  # (10, 20, 30)
    fn2 = lambda **kwargs: kwargs
    print(fn2(name='python', age=20))  # {'name': 'python', 'age': 20}
    fn3 = lambda a,b: a if a > b else b
    print(fn3(10,20))
    # 列表数据按字典key值排序
    students = [
        {'name': 'Sam', 'age': 20},
        {'name': 'Tom', 'age': 19},
        {'name': 'Jack', 'age': 22},
    ]
    # 按照name值升序
    students.sort(key=lambda x:x['name'])
    print(students)

    # 按照age值升序
    students.sort(key=lambda x: x['age'])
    print(students)