#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/13/2022 6:29 PM
@file:8-2-闭包使用.py
@project:openpyxl_excel
"""
# 根据配置，使用闭包实现不同人的对话
if __name__ == "__main__":
    # 外部函数接收姓名参数
    def config_name(name):
        # 内部函数保存外部函数的参数，并且完成数据显示的组成
        def inner_func(msg):
            print(name + ':' + msg)    # 这个name是外部函数的参数，内部函数也使用，相当于保存了外部函数的变量
        return inner_func
    # 创建闭包实例，即获取闭包
    tom = config_name('tom')
    # 执行tom闭包
    tom('哥们，过来一下')   # tom:哥们，过来一下
    # 创建jerry闭包实例
    jerry = config_name('jerry')
    jerry('我不去')   # 里面的参数传递给inner_func
    # 再次执行tom闭包，形成一个对话
    tom('来吧')
