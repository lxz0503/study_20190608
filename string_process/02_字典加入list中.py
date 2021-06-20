from collections import Counter
# 统计字典中value出现的次数，并排序输出
counts = {'lixiaozhan': 2, 'beijing': 2, 'jiaotong': 1, 'university': 3, 'shanghai': 3, 'zhangsan': 1, 'nanjing': 2}
# items = list(counts.items())
items = Counter(counts)
print(items.most_common())   # 统计字典中value出现的次数，并排序输出
# 统计一个列表中元素出现的次数，并输出
test = ['lixiaozhan', 'beijing', 'beijing', 'jiaotong', 'university', 'shanghai', 'shanghai', 'zhangsan', 'nanjing']
res = Counter(test)
print('res:', res.most_common(3))
#
# 统计单词出现的次数
counts = {}
words = ["aa", "aa", "bb", "bb", "c", "c", "c"]
for word in words:
    counts[word] = counts.get(word, 0) + 1
        # 字典中get函数用法,返回指定键的值，如果指定键的值不在字典中返回指定值(本例子中指定值为0)，默认为 None。
print("the dictionary is %s" % counts)
items = list(counts.items())  # Python 字典(Dictionary) items() 函数以列表返回可遍历的(键, 值) 元组数组,list函数再把其转化为list
print("the list is %s" % items)
items.sort(key=lambda x: x[1], reverse=True)
print("the sorted list is %s" % items)
for i in range(3):
    word, count = items[i]
    # print("{0:<5}->{1:>5}".format(word, count))
    print("word %s occurred----%s times" % (word, count))

#
sub = {
    'doc': ['.pdf', '.rtf', '.txt'],
    'audio': ['.mov', '.m4b', '.mp3'],
    'image': ['.jpg', '.jpeg', '.png']
}
print(sub.items())
# dict_items([('doc', ['.pdf', '.rtf', '.txt']), ('audio', ['.mov', '.m4b', '.mp3']), ('image', ['.jpg', '.jpeg', '.png'])])
# for cat, suffixes in sub.items()