# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发团队   ：明日科技
# 开发人员   ：小科
# 开发时间   ：2019/4/8  14:21 
# 文件名称   ：sortFiles.PY
# 开发工具   ：PyCharm
'''
  运营数据文件的分类整理,把文件整理到根据文件名前三个字符命名的目录里面
'''
import os
import shutil             # 导入shutil模块，用来移动文件
while True:            # 循环输入
    path = input('请输入要整理文件所在路径：')    # 记录输入的路径
    try:
        list_dir = os.listdir(path)  # 遍历选择的文件夹
        for i in range(0, len(list_dir)):  # 遍历文件列表
            filepath = os.path.join(path, list_dir[i])  # 记录遍历到的文件名(包括路径)
            if os.path.isfile(filepath):       # 判断是否为文件,只有是文件才会进行处理
                dirname = list_dir[i][0:3]      # 获取文件名的前3个字符串，用来作为文件夹名
                dirpath = os.path.join(path, dirname)     # 拼接文件夹路径
                if not os.path.exists(dirpath):          # 判断文件夹路径是否存在
                    os.mkdir(dirpath)                # 创建文件夹
                # 移动文件进行整理
                shutil.move(filepath, os.path.join(dirpath, list_dir[i]))
        print('整理完成……')
    except Exception as e:
        print(e)