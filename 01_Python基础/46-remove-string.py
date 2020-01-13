#!/usr/bin/env python3
# coding=utf-8
# 移除字符串中不需要的字符

# strip(),lstrip(),rstrip(), 只能删除两端不需要的字符
s = '----****123 abc  '
print(s)
# n = s.strip()
print(s.lstrip('-*'))
# 删除单个固定位置的字符，可以用切片加拼接的方法
s = 'abc:123'
print(s[:3] + s[-3:])

# 删除多个位置的相同字符，可以用replace
s = '\tabc\t123\txyz'
print(s.replace('\t', ''))   # 注意替换符不是空格

# 删除或者替换多个位置的不同字符，可以用re.sub
import re
s = '\tabc\t123\txyz*f\rff*\r'
print(re.sub('[\t\r*]', ' ', s))   # 注意是用空格替换

# 字符串的maketrans()，类似于密码本
d = {'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5', 's': ' ', '\t': ' ', '\r': ''}
trantab = str.maketrans(d)
st = 'just \tdo \rit'
print(st.translate(trantab))    # ju6t 4o it