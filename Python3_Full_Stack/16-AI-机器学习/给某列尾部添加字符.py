#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/9/2022 3:07 PM
@file:给某列尾部添加字符.py
@project:xiaozhan_git
"""
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv('a.csv')
    df['A'] = df['A'].map(lambda x: f'{x}今天关注了早起Python')
    df.to_csv('b.csv', header=True, index=None)
