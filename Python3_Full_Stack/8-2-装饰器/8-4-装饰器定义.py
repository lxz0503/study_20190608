#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/13/2022 9:16 PM
@file:8-4-装饰器定义.py
@project:openpyxl_excel
"""
if __name__ == "__main__":
    # 定义装饰器
    def decorator(func):
        def inner():
            # 在内部函数里面对已有函数进行装饰
            print('已经添加登录验证')
            func()
        return inner

    # 原始函数，仅仅有发表评论功能，接下来给它用装饰器
    @decorator
    def comment():     # comment函数就作为参数传递给func
        print('发表评论')

    # 调用装饰器对函数进行装饰
    # comment = decorator(comment)     # comment就是inner()函数
    # 上面这端封装，等价于在comment()函数前面添加 @decorator
    # 函数调用,不改变调用方式
    comment()
