#!/usr/bin/env python3
# coding=utf-8

from tempfile import TemporaryFile,NamedTemporaryFile

f = TemporaryFile()
f.write(b'abcded' * 1000)    # 写到磁盘,注意必须是二进制形式写入
f.seek(0)   # 准备读取文件内容
print(f.read(100))
print(f.read(100))
f.close()    # 关闭的同时也删除了临时文件

# 能查到临时文件名的操作
f = NamedTemporaryFile()
print(f.name)         # C:\Users\ADMINI~1\AppData\Local\Temp\tmp7l_1xtgy
f.write(b'abcded' * 1000)    # 写到磁盘,注意必须是二进制形式写入
f.seek(0)   # 准备读取文件内容,不要一次读取太多，占内存太大
print(f.read(100))
print(f.read(100))
f.close()    # 关闭
print(f.name)
f.delete()


