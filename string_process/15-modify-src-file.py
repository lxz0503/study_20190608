#!/usr/bin/env python3
# coding=utf-8
# 直接用python正则表达式改变文件内容,用循环来支持修改多处内容
import os
import re

class ModifyFileContent(object):
    def __init__(self, file_name, to_modify):
        self.file_name = file_name
        self.to_modify = to_modify

    def modify_file(self):
        for content in self.to_modify:
            src_code, new_code = content[0], content[1]
            with open(self.file_name, 'r') as f:
                with open('file_name.bak', 'w') as f1:
                    for line in f:
                        f1.write(re.sub(src_code, new_code, line))
            os.remove(self.file_name)
            os.rename('file_name.bak', self.file_name)


if __name__ == '__main__':
    file_name = 'reg_text'     # 要修改的文件名
    to_modify = [              # 文件里要修改的内容，放在列表里，每个元素又是一个列表
        ['timestamp', 'lixiaozhan'],   # 前面是未修改前，后面是修改后
        ['lastS', 'lixiaozhan']
    ]
    ts = ModifyFileContent(file_name, to_modify)
    ts.modify_file()
