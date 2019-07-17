# 统计字符串中每个字符出现的次数
import collections


test_str = "hello world"
count_dict = dict(collections.Counter(test_str))
print(count_dict)    # {'h': 1, 'e': 1, 'l': 3, 'o': 2, ' ': 1, 'w': 1, 'r': 1, 'd': 1}

# 统计字符串中出现次数最多的字符

from collections import Counter

s = 'heLLoworldabbbaaaccc'
#s = input()                     # 从控制台输入字符串
c = Counter(s)
# [('a', 4), ('b', 3), ('c', 3), ('L', 2), ('o', 2)]
print(c.most_common(5))         # 获取频率最高的5个字符，存储在列表,如果没有设置参数，就默认全部统计
print(c.most_common(5)[0][0])   # 打印列表第一个元素. a
print(c.most_common(5)[0][1])   # 出现的次数, 4

# {'h': 1, 'e': 1, 'l': 3, 'o': 2, ' ': 1, 'w': 1, 'r': 1, 'd': 1}
# [('a', 4), ('b', 3), ('c', 3), ('L', 2), ('o', 2)]
# a
# 4

# [('a', 4), ('l', 3), ('b', 3), ('c', 3), ('o', 2)]
# a
# 4