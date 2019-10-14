# coding=utf-8
import json

# 读取数据
with open('quotes.json', 'r') as f:
    data = json.load(f)
print(type(data))           # 注意这个比较特殊，是一个list，但是每个list元素是字典
for k in data:
    # print(type(k))          # 这个是字典格式
    # print(k)
    for i in k:
        print('key name is %s,value is %s' % (i, k[i]))

# for jl,统计一下有多少条记录
for count, line in enumerate(open('quotes.jl', 'r'), start=1):
    pass
print(count)

# 处理后缀是jl格式的爬虫文件
with open('items.jl', 'r') as f:
    lines = f.readlines()
    for line in lines:
        # print(eval(line))    # 已经是字典类型数据了
        for k in eval(line):
            print(k, eval(line)[k])

