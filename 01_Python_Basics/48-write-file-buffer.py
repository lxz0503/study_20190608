#!/usr/bin/env python3
# coding=utf-8
# 文件内容先写入缓冲，然后再存入磁盘，用到I/O操作
# 需要先写入buffer，否则频繁调用I/O操作
# buffering大于1就是全缓冲，
f = open('file_test_buffer', 'w', buffering=2048)
f.write('+'*2048)
f.close()
# 此时在另一个终端，tail -f filename直到写入2048字节后才能显示文件内容

# 行缓冲
f = open('file_test_buffer', 'w', buffering=2048)
f.write('aaaa')
f.write('bbbbb')
f.write('\n')   # 直到写入换行符才会显示文件内容，即真正写到磁盘
f.close()
# 此时在另一个终端，tail -f filename直到写入换行符后才能显示文件内容，即写进了磁盘

# 无缓冲就是把buffering=0,，这种适合用在串口输出
#
# linux command
# dd if=/home/windriver/1.txt of=/home/windriver/abc/2.txt bs=1024 count=1024

