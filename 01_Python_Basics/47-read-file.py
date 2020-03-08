#!/usr/bin/env python3
# coding=utf-8
# 在文本文件中，没有使用b模式选项打开的文件，只允许从文件头开始计算相对位置，从文件尾计算时就会引发异常
# seek() 方法用于移动文件读取指针到指定位置。
# seek() 方法语法如下：
# fileObject.seek(offset[, whence])
# 参数
# offset -- 开始的偏移量，也就是代表需要移动偏移的字节数，如果是负数表示从倒数第几位开始。
# whence：可选，默认值为 0。给 offset 定义一个参数，表示要从哪个位置开始偏移；
# 0 代表从文件开头开始算起，1 代表从当前位置开始算起，2 代表从文件末尾算起。
f = open('file_test', 'rb')   # 注意必须是rb模式读取
f.seek(1)
line = f.read(10)
print(line)
f.seek(0, 0)     # 重新设置文件读取指针到开头
print(f.read(1))
# b'good boy\r\n'
f.seek(-10, 2)     # 移动到文件倒数第10个字节
print(f.read(20))  # 这里的read参数最多只能读取10个字节，即使设置为20

# f.tell()返回文件指针当前位置
f.seek(0, 2)       # 将文件指针移动到文件结尾
print(f.tell())    # 184, 然后能算出文件总的长度，即字节数
