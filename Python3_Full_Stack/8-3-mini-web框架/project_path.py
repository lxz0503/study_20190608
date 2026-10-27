#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/18/2022 6:42 PM
@file:project_path.py
@project:openpyxl_excel
"""
import os
def projectPath():
    # print(os.path.realpath(__file__))
    # print('a', os.path.split(os.path.realpath(__file__)))
    return os.path.split(os.path.realpath(__file__))[0].split('tools')[0]

if __name__ == "__main__":
    print(projectPath())