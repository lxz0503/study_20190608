counts = {'lixiaozhan': 2, 'beijing': 2, 'jiaotong': 1, 'university': 3, 'shanghai': 3, 'zhangsan': 1, 'nanjing': 2}
items = list(counts.items())
print(items)
items.sort(key=lambda x: x[1], reverse=True)  # 用list内置的sort方法按照第二个元素排序,逆序
print("the sorted list is %s" % items)

for i in range(5):
    word, count = items[i]     # 每个list元素是一个元组
    # print("{0:<5}->{1:>5}".format(word, count))
    print("%s----%s" % (word, count))