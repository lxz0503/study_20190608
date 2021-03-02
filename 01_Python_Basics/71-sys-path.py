#!/usr/bin/env python3
# coding=utf-8

# https://blog.csdn.net/raby_gyl/article/details/82390338
# python程序中使用 import XXX 时，python解析器会在当前目录、已安装和第三方模块中搜索 xxx，如果都搜索不到就会报错。
# 使用sys.path.append()方法可以临时添加搜索路径，方便更简洁的import其他包和模块。这种方法导入的路径会在python程序退出后失效。

# 1. 加入上层目录和绝对路径
# import sys
# sys.path.append('..') #表示导入当前文件的上层目录到搜索路径中
# sys.path.append('/home/model') # 绝对路径
# from folderA.folderB.fileA import functionA
# 2. 加入当前目录
# import os,sys
# sys.path.append(os.getcwd())
# os.getcwd()用于获取当前工作目录
# 3. 定义搜索优先顺序
# import sys
# sys.path.insert(1, "./model")
# sys.path.insert(1, "./crnn")定义搜索路径的优先顺序，序号从0开始，表示最大优先级，sys.path.insert()加入的也是临时搜索路径，程序退出后失效

import sys

# 如果想导入自己写的包的时候更方便，也就是不写全路径，可以用上面的方法，append或者insert
# 参考下面的例子

# xiaozhan    below is the config file
# hyan1@pek-vx-nwk1:/buildarea1/hyan1/vxworks7/helix/guests/vxworks-7/pkgs_v2/net/ipnet/NOT_IMPORTED/iptestengine/src$ ls ../config/config.py
# ../config/config.py*
# hyan1@pek-vx-nwk1:/buildarea1/hyan1/vxworks7/helix/guests/vxworks-7/pkgs_v2/net/ipnet/NOT_IMPORTED/iptestengine/src$ vi ../config/config.py

sys.path.insert(0, '../config')
import config    # 想导入这个包,但是当前执行路径不是config.py所在路径