# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发团队   ：明日科技
# 开发人员   ：小科
# 开发时间   ：2019/4/8  10:28 
# 文件名称   ：openfile.PY
# 开发工具   ：PyCharm
'''
  如何调用系统默认程序打开相应文件
'''
import os
while True:
    try:
        path = input('请输入文件所在路径：')    # 记录输入的文件路径, 例如D:\\log.txt
        os.startfile(path)                      # 调用系统程序打开文件
    except Exception as e:
        print(e)
        # print('请输入正确的文件路径……')
