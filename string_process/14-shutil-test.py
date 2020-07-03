#!/usr/bin/env pytyon3
# coding=utf-8
# 只适用于在本地一台机器复制或者移动文件
import shutil

src = '1.txt'
dst = '2.txt'
# shutil.copyfile(src, dst)
shutil.copyfile('%s' % src, '%s' % dst)

# shutil.move(src, dst)