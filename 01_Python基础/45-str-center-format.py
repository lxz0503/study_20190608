#!/usr/bin/env python3
# coding=utf-8
# 字符串的对齐，格式化输出

dic = {
    'local': 100.0,
    'SmallCull': 0.04,
    'DisxtCull': 500.0,
    'trilinear': 40,
    'farclip': 477
}
# 求key的最大宽度
width = max(map(len, dic.keys()))
print(width)

for k in dic:
    print('%10s: %5s' % (k, dic[k]))   # 默认是采用右对齐格式，10s表示宽度为10个字符
#　左对齐格式
print('left format:')
for k in dic:
    print('%-10s: %-5s' % (k, dic[k]))   # 加上负号表示对齐格式，10s表示宽度为10个字符
#
print('使用ljust方法：')
for k in dic:     # 注意下面必须用str()先转化为字符串格式，才能使用ljust()方法,第二个参数为填充字符
    print('%s: %s' % (k.ljust(10, '*'), str(dic[k]).ljust(5)))

# 居中对齐
print('使用center方法：')
for k in dic:     # 注意下面必须用str()先转化为字符串格式，才能使用center()方法,第二个参数为填充字符
    print('%s: %s' % (k.center(10, '*'), str(dic[k]).center(5)))
# format方法,<>^分别表示左，右，居中对齐
print('使用format方法：')
for k in dic:     # 注意下面必须用str()先转化为字符串格式
    print('{:9} {} {:*>5}'.format(k, ':', str(dic[k])))   # 默认是左对齐
