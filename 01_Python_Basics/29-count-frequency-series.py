#!/usr/bin/env python3
# coding=utf-8
# 统计一个序列中元素出现的次数，结果必然是字典形式

from random import randint

data = [randint(0, 20) for i in range(30)]   # 数字介于0到20之间，一共30个元素
# print(len(data))
# 以data中的数值为key创建 一个字典，每个初始值为0
# 字典的key不能重复，所以自动过滤掉了重复的key,即不会重复统计
c = dict.fromkeys(data, 0)
# print(c)
for x in data:
    c[x] += 1
print(c)
# 统计出现频率最高的前5个元素
items = list(c.items())
items.sort(key=lambda x: x[1], reverse=True)
# print("the sorted list is %s" % items)
for i in range(5):
    word, count = items[i]
    # print("{0:<5}->{1:>5}".format(word, count))
    print("%s----%s" % (word, count))

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
