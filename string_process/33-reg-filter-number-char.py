#!/usr/bin/env python3
# coding=utf-8
# remove specific character and number

import re

a = "not 404 found 50.01 张三 99 深圳"
l = a.split(" ")
print(l)
res = re.findall(r'\d+\.?\d+|[a-zA-Z]+', a)
print(res)

for i in res:
    if i in l:
        l.remove(i)
new_str = " ".join(l)
print(new_str)