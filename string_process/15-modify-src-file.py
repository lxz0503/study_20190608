#!/usr/bin/env python3
# coding=utf-8
# 直接用python正则表达式改变文件内容,支持修改多处内容
import os
import re


def modify_file(file_name, src_code, new_code):
    with open(file_name, 'r') as f:
        with open('file_name.bak', 'w') as f1:
            for line in f:
                f1.write(re.sub(src_code, new_code, line))
    os.remove(file_name)
    os.rename('file_name.bak', file_name)


if __name__ == '__main__':
    file_name = 'reg_text'
    modify_content = [
        ['timestamp', 'lixiaozhan'],
        ['lastS', 'lixiaozhan']
        ]
    for content in modify_content:
        modify_file(file_name, content[0], content[1])
