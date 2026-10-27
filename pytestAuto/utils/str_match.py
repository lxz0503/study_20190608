#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/1/2022 5:06 PM
@file:str_match.py
@project:xiaozhan_git
"""
import re

tst = '[  5]   0.00-20.00  sec   588 MBytes   940 Mbits/sec                  receiver'
pat = re.compile(r"(\d+) Mbits/sec")
res = pat.search(tst)
if res is not None:
    print(res.group().split()[0])   # this is a string type


