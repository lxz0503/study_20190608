#!/usr/bin/env python3
# coding=utf-8
# 统计一个序列中元素出现的次数，结果必然是字典形式

from random import randint

data = [randint(0, 20) for i in range(30)]   # 数字介于0到20之间，一共30个元素
# print(len(data))
# 以data中的数值为key创建 一个字典，每个初始值为0
# 字典的key不能重复，所以自动过滤掉了重复的key,即不会重复统计
c = dict.fromkeys(data, 0)  # default value is 0
print(c)   #
print(data)  # data includes duplicated element
for x in data:
    c[x] += 1   # change the dict value
print(c)
# {20: 0, 19: 0, 12: 0, 2: 0, 16: 0, 18: 0, 1: 0, 13: 0, 7: 0, 8: 0, 0: 0, 15: 0, 14: 0, 9: 0, 17: 0, 3: 0}
# [20, 19, 12, 2, 16, 19, 18, 1, 13, 19, 7, 7, 13, 20, 8, 0, 18, 15, 14, 0, 19, 0, 9, 16, 12, 16, 17, 3, 19, 1]
# {20: 2, 19: 5, 12: 2, 2: 1, 16: 3, 18: 2, 1: 2, 13: 2, 7: 2, 8: 1, 0: 3, 15: 1, 14: 1, 9: 1, 17: 1, 3: 1}
# 统计出现频率最高的前5个元素
items = list(c.items())
items.sort(key=lambda k: k[1], reverse=True)
# print("the sorted list is %s" % items)
for i in range(5):
    word, count = items[i]   # unpack
    # print("{0:<5}->{1:>5}".format(word, count))
    # print("%s----%s" % (word, count))
    print(f'{word}---occurs---{count}---times')

# you can also use Counter, this method is more simple

from collections import Counter
c2 = Counter(data)
# print(c2[10])    # c2的类型也类似于一个字典，所以也能用键值对来访问
print('出现频率最高的前5个元素:\n%s' % c2.most_common(5))

# 统计文本中的词频
import os,re
f_dir = os.path.dirname(__file__) + '/1.txt'
# 把整个文本作为一个字符串读进来
txt = open(f_dir, "r", encoding='UTF-8').read()
# 以非字母 \W+ 正则表达式来分隔，得到一个包含每个单词的列表,然后把列表作为参数传递给Counter()
c3 = Counter(re.split('\W+', txt))
print('出现频率最高的前5个单词:\n%s' % c3.most_common(5))
#
c = Counter()
with open('file_test', 'r') as f:
    for line in f:
        c[line] += 1
print(c.most_common(2))
