# 统计字符串中每个字符出现的次数
import collections


test_str = "hello world"
count_dict = dict(collections.Counter(test_str))
print(count_dict)

# 统计字符串中出现次数最多的字符

from collections import Counter

# s = 'helloworldabbbaaaccc'
s = input()                     # 从控制台输入字符串
c = Counter(s)
print(c.most_common(5))         # 获取频率最高的5个字符，存储在列表
print(c.most_common(5)[0][0])   # 打印列表第一个元素
print(c.most_common(5)[0][1])   # 出现的次数

# [('a', 4), ('l', 3), ('b', 3), ('c', 3), ('o', 2)]
# a
# 4