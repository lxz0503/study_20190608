# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发团队   ：明日科技
# 开发人员   ：小科
# 开发时间   ：2019/4/11  16:35 
# 文件名称   ：autoinstallmodule.PY
# 开发工具   ：PyCharm
'''
  解决由于未安装模块而导致的“No module named '***'”问题
'''
import os
try:
    import jieba # 导入模块
except ModuleNotFoundError:
    print('正在安装jieba，请稍等...')
    os.system('pip install jieba') # 安装jieba模块
