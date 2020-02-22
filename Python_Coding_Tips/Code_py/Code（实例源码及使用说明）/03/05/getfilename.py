# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发团队   ：明日科技
# 开发人员   ：小科
# 开发时间   ：2019/4/8  10:39 
# 文件名称   ：getfilename.PY
# 开发工具   ：PyCharm
'''
  批量提取文件名保存到一个文件中
'''
import os

with open('Test.txt', 'a') as f:                       # 以追加方式打开文件
    path = input('请输入要提取名称的文件所在路径：')       # 记录输入的路径, 例如 D:\BBC
    try:
        list_dir = os.listdir(path)              # 遍历选择的文件夹
        for i in range(0, len(list_dir)):         # 遍历文件列表
            filename = os.path.splitext(list_dir[i])[0]         # 提取文件名.例如 a.exe，会提取a，自动去掉后缀
            f.write(filename + '\n')                            # 将提取的文件名写入文本文件
        print('文件名提取完成 ')
    except Exception as e:
        print(e)