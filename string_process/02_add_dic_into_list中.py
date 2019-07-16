counts = {'lixiaozhan': 2, 'beijing': 2, 'jiaotong': 1, 'university': 3, 'shanghai': 3, 'zhangsan': 1, 'nanjing': 2}
items = list(counts.items())
print(items)
items.sort(key=lambda x: x[1], reverse=True)
print("the sorted list is %s" % items)

for i in range(5):
    word, count = items[i]
    # print("{0:<5}->{1:>5}".format(word, count))
    print("%s----%s" % (word, count))