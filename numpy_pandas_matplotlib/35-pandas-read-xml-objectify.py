#!/usr/bin/env python3
# encoding=utf-8

# https://blog.csdn.net/qq_39192827/article/details/93990652  pandas 读取各种格式文件的小例子

import pandas as pd
from lxml import objectify

xml = objectify.parse('test.xml')
# 可以通过元素树的getroot()方法获取根，即最外一层的data。此时root类型名即为最外层标签名
root = xml.getroot()
print(root.student.name)    # zhangsan
mes1 = root.student.getchildren()
print('first student获取的子标签内容：', mes1)     # ['zhangsan', 24, 'shanghai']

mes2 = root.student[1].getchildren()
print('second student获取的子标签内容：', mes2)     # ['lisi', 12, 'beijing']

print([child.tag for child in mes1])  # 获取子标签
print([child.tag for child in mes2])  # 获取子标签



