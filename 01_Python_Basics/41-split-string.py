#!/usr/bin/env python3
# coding=utf-8
# 拆分有多种分隔符的字符串
import re
s = 'ab;cd|efg|hi,jk|mn\top;rst,/xyz'   # 注意这里  \t也是分隔符
print(s)
new_s = re.split(r'\W+', s)    # \W+ 代表非字母
print(new_s)
#

new_s = re.split(r'[\t,;/|?!]+', s)    # \W+ 代表非字母
print(new_s)