# 找出list重复元素的方法
# 原文链接：https://blog.csdn.net/qq_41551919/article/details/83060738

from collections import Counter
L = [3, 2, 4, 6, 5, 3, 6, 1]
# 使用集合中的Counter
print(type(Counter(L).items()))
print(Counter(L).items())
duplicate = {key: count for key, count in Counter(L).items() if count > 1}     # Counter(L).items()，必须转成这种才能迭代
print(duplicate)
# print({key: count for key, count in Counter(L).items() if count > 1})
# {6: 2}

# 或遍历列表,三元表达式，返回一个字典
duplicate = {i: L.count(i) for i in L if L.count(i) > 1}
print(type(duplicate))     # it is dict
print(duplicate)
# {6: 2}
# {3: 2, 6: 2}
# <class 'dict'>
# {3: 2, 6: 2}

