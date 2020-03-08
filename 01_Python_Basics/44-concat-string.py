#!/usr/bin/env python3
# coding=utf-8
# 网络通信中发送UDP数据包,必须按照顺序拼接

# 用最简单的多个字符串相加的办法，实际上是运算符重载
s1 = 'abcd'
s2 = '12345'
s = s1 + s2   # 实际上是运算符重载，调用了str.__add__(s1,s2)方法
# print(s)

pl = ['<0112>', 23, '<1024*768>', '<500.0>']
s = ''
for p in pl:
    s += str(p)     # 每次都生成一个临时列表，开销很大，如果列表很大，浪费资源
    # print(s)
print(s)
# 方法二，用str.join(), 生成器表达式可以节省开销，join方法的参数必须是字符串
l = ''.join(str(x) for x in pl)      # l = '*'.join(pl)
print(l)
