"""
统计文本中的每个单词数目，下面是统计出现最多的单词数目
把文件用记事本打开，另存为UTF-8编码格式
"""
#!/usr/bin/env python3
# coding=utf-8
import os

def get_text():
    f_dir = os.path.dirname(__file__) + '/1.txt'
    txt = open(f_dir, "r", encoding='UTF-8').read()
    txt = txt.lower()
    for ch in '!"#$%&()*+,-./:;<=>?@[\\]^_‘{|}~':
        txt = txt.replace(ch, " ")      # 将文本中特殊字符替换为空格
    return txt


file_txt = get_text()
words = file_txt.split()    # 对字符串以空格进行分割，获得单词列表
counts = {}      # 初始化空字典，用来存储单词和单词数目
for word in words:
    # if len(word) == 1:
    #     continue
    # else:
    # if len(word) != 0:
    counts[word] = counts.get(word, 0) + 1
        # 字典中get函数用法,返回指定键的值，如果指定键的值不在字典中返回指定值(本例子中指定值为0)，默认为 None。
print("the dictionary is %s" % counts)
items = list(counts.items())  # Python 字典(Dictionary) items() 函数以列表返回可遍历的(键, 值) 元组数组,list函数再把其转化为list
print("the list is %s" % items)
items.sort(key=lambda x: x[1], reverse=True)
print("the sorted list is %s" % items)

for i in range(5):
    word, count = items[i]
    # print("{0:<5}->{1:>5}".format(word, count))
    print("%s----%s" % (word, count))
