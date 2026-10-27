#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:10/10/2022 10:16 AM
@file:run_js.py
@project:xiaozhan_git
"""
import execjs
import os
print(execjs.get().name)  #
# 'PyV8'
# os.environ["EXECJS_RUNTIME"] = 'Node'  #
tmp = os.path.dirname(__file__) + '/test.js'
with open(tmp) as f:  # 执行 JS 文件
    ctx = execjs.compile(f.read())
    print(ctx.call('add', 1, 2))
