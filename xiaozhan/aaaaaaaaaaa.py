import os
import re

s = "./IKEMain.log:0xffff8000005b7850 (tLogin55dc70): The task been terminated because it triggered an exception that raised the signal 11"

c = s.count('th')

#查看函数定义，参数里面带=号的可以不要，但是没有=的必须要传入参数
print(c)
m = re.search("exception", s)
if m is not None:
    print(m.group())
    print(m.group().upper())
    print(m.group().lower())


config = ' -add '.join(['_WRS_CONFIG_COMPONENT_IPDHCPS=y',
                            '_WRS_CONFIG_COMPONENT_IPIKE=y',
                            '_WRS_CONFIG_COMPONENT_IPIPSEC=y',
                            '_WRS_CONFIG_COMPONENT_IPMCP=y',
                            '_WRS_CONFIG_COMPONENT_IPRIP=y',
                            '_WRS_CONFIG_COMPONENT_IPFIREWALL=y',
                            '_WRS_CONFIG_COMPONENT_FEATURE_IPNET_INET6=y'])
print(config)

if "IPIKE" in config:
    print("true")
# 下面的字符串格式化，{}是占位符，格式化就是将占位符里面的内容替换为其他内容
#test = "I am {name},age {a}"
#v = test.format(name="alex", a=19)

# 下面的等同于上面的实现
test = "I am {0},age {1}"
v = test.format("alex",19)
print(v)

#
test = "aaa222"
v = test.isalpha()
print(v)

test = {
    "netifs": [
        {
            "device": {
                "name": "gei",
                "unit": 0,
                "id": "gei0"
            },
            "inet": {
                "address": "30.1.1.5",
                "prefixlen": 24,
                "gateway": "30.1.1.1"
            }
        }
     ]
}
print(type(test))

# expandtabs()    set the size of the tab，以\t作为分隔符

test = "username\temail\tpassword\n" \
       "beijing\tbeijing@123c.om\t123\n" \
       "shanghai\tshanghai@234.com\t234\n" \
       "shenzhen\tshenzhen@456.com\t456"
v = test.expandtabs(20)
print(v)
#
test = "aLex"
v = test.swapcase()
v = test[0:-1]  # aLe
print(v)

v = range(10)
for item in v:
    print(item,end="#")
print()

#如果列表里既有数字又有字符串，只能通过for循环来操作，转换成字符串
#如果只有字符串，就直接用"".join(列表名字)转换成字符串
s = ""
l = [1,23,"sss"]
for i in l:
    s = s + str(i)
print(s)

# v = l.clear()
# print(l)

li = [1,2,3,"aa"]
l.extend(li)
print(l)      # [12, 23, 'sss', 1, 2, 3, 'aa']

a = [1,2,3]
b = [1,2,3]
# c = a + b
a.extend(b)    # this is equal with c = a + b
print(a)

v = l.index(2)
print(v)

l.pop()   # remove the last value
print(l)    # [12, 23, 'sss', 1, 2, 3]

l.remove(1)   # remove the first 1 if you have multiple 1
print(l)

# tuple can not be added, removed,modified.

# 字典,key如果设置为1等同于设置为True，键值不能重复
info = {
    "a": 100,
    "beijing": 200,
    2: "aaaa",
    True: 300,
}

for item in info.values():
    print(item) # print the value

for item in info:
    print(item, info[item])  # item is the key

for item in info.items():
    print(item)
    # print(type(item))   # it is tuple like (True, 300)

for k, v in info.items():
    print(k, v)  # it is not tuple, but just a 100
#dict   (ctrl+shift+i，可以快速查看dict的实现)

v = info.get("a")
print(v)
v = info.get(True)
print(v)
v = info.get("aaaaa", 10)    # if this key aaaaa does not exist, then return 10
print(v)

# info.pop(True)   # True is the key that will be removed
# print(info)

v = info.pop("aaaaaa", 100)  # if key "aaaaa" is not found, then return 100
print(info)
print(v)

# if key "a" is found, return the value in the dictionary. if key "a" is not found, return the value 500
v = info.setdefault("a", 500)
print(v)

v = info.setdefault("b", 500)  # if key "b" is not found, add this key-value into the dict
print(v)
print(info)    # {'a': 100, 'beijing': 200, 2: 'aaaa', True: 300, 'b': 500}

n = 9
count = 0
for i in range(1, n):
    for k in range(1, n):
        if i != k:
            count += 1
print(count)

#
print("aa", "bb", "cc",)   # 默认分隔符就是空格  aa bb cc

# 5,3,3   100，公鸡 母鸡 小鸡，用100文钱，买100只，小鸡是1文钱3只，
for x in range(1,100//5):     # 公鸡最多买100//5只
    for y in range(1,100//3):   # 母鸡最多能买100//3
        for z in range(1,100):  # 小鸡最多能买100只
            if x + y + z == 100 and x*5 + y*3 + z/3 == 100:
                print(x,y,z)

#
li = ["alex", "rain", 123]
l = []
for item in li:
    l.append(str(item))

print(l)
v = "_".join(l)
print(v)

#
seasons = ['Spring', 'Summer', 'Fall', 'Winter']
print(len(seasons))
v = list(enumerate(seasons))
print(v)
# [(0, 'Spring'), (1, 'Summer'), (2, 'Fall'), (3, 'Winter')]
v = list(enumerate(seasons, start=1))       # 下标从 1 开始
print(v)
# [(1, 'Spring'), (2, 'Summer'), (3, 'Fall'), (4, 'Winter')]

seq = ['one', 'two', 'three']
for i, element in enumerate(seq):
    print(i, element)

# 0 one
# 1 two
# 2 three
# 下面的元组，第一级元素不能修改，但是可以修改里面的二级元素
# k2对应的列表可以修改，但是k3对应的元组不能修改
tu = ("alex",
      [11, 22,
       {"k1": 'v1', "k2": ["age","name"], "k3":(11, 22, 33)},
       44
       ]
      )
print(type(tu))
tu[1][2]["k2"].append("address")
print(tu[1][2]["k2"])
# 找到数组中两个数之和等于目标值对应的元素，放到集合中
def two_sum(numbers, target):
    l = []
    for i in range(len(numbers) - 1):  # 循环到倒数第二位
        for j in range(i + 1,len(numbers)): # 从i往后开始循环
            if (numbers[i] + numbers[j]) == target:
                l.append((numbers[i], numbers[j]))
    return l

# ret = two_sum([2,7,11,15],18)
# print(type(ret))
print(two_sum([1,2,3,4], 5))

# lambda
# x 是形参，冒号后面是函数体
func = lambda x: x+1
print(func(10))

name = "aaaa"
func = lambda x: x + "_sb"
res = func(name)
print("lambda result is", res)

func = lambda x, y, z: (x+1, y+1, z+1)
res = func(1, 2, 3)   # return is tuple
print("the result is", res)
print(type(res))

# map() 会根据提供的函数对指定序列做映射。
# 第一个参数 function 以参数序列中的每一个元素调用 function 函数，返回包含每次 function 函数返回值的新列表

def square(x):  # 计算平方
    return x ** 2

map(square, [1, 2, 3, 4, 5])  # 计算列表各个元素的平方
# [1, 4, 9, 16, 25]
map(lambda x: x ** 2, [1, 2, 3, 4, 5])  # 使用 lambda 匿名函数
#[1, 4, 9, 16, 25]

# 提供了两个列表，对相同位置的列表数据进行相加
map(lambda x, y: x + y, [1, 3, 5, 7, 9], [2, 4, 6, 8, 10])
# [3, 7, 11, 15, 19]

#
print(abs(-2))

# 三元表达式与列表解析
# 三元就是三个运算符
# 变量 = 值-if条件-else 值二
l = []
for i in range(10):
    l.append("egg%s" % i)
print(l)

l = ["egg%s" % i for i in range(10)]
print(l)
# 三元表达式,生成列表
# 主体是for循环，二元是"egg%s" % i,3元是判断
# 其实就是把几行的内容精简一下，写到一行
l = ["egg%s" % i for i in range(10) if i > 5]
print(l)

#如果列表内容特别大，就用生成器表达式，把[]替换为()即可

l = (i for i in range(10))
print(l)  # <generator object <genexpr> at 0x000000000213F780>
print(l.__next__())   # 这里输出0
print(l.__next__())   # 这里输出1

# yield相当于函数里面的return

def test():
    print("first")
    yield "the first"
    print("second")
    yield 2
    print("third")
    yield 3
res = test()
print(res.__next__())  # 这里输出1
print(res.__next__())  # 这里输出2

#
def product():
    for i in range(10):
        print("start to produce")
        yield "product %s is ok" % i  # 不会显示在输出内容里面
        print("start to sell product %s" % i)
pro = product()  # pro就是一个生成器,generator
for jidan in pro:
    print(jidan)

# buyer1 = pro.__next__()   # 有人买，就生产
# buyer1 = pro.__next__()
# buyer1 = pro.__next__()
# buyer1 = pro.__next__()

l = sum(i for i in range(10))  # 用迭代器求和
print(l)

l = sum([i for i in range(10)])  # 用普通列表三元表达式解析列表
print(l)  # 对列表求和

# 使用yield的好处是一次不用读取所有数据，否则会占用很大内存

def get_population():
    with open("population_statistics", "r") as f:
        for i in f:
            yield i  # 类似于readline，但是每次只读一条数据

g = get_population()     # g is a generator
print(g)    # <generator object get_population at 0x00000000028871A8>
#
# for p in g:
#     p_dic = eval(p)
#     print("the population of each city", p_dic["population"])
# sum
all_pop = sum(eval(i)['population'] for i in g)   # sum函数，求和，用生成器
print("the sum is", all_pop)
#
for p in g:    # 生成器只能迭代一次,所以这次不生效
    print("the portion of each city is ", eval(p)['population']/all_pop)
# population = eval(g.__next__())
# print(type(g.__next__()))  # it is str
# print(type(population)) `127  # it is dict
# print("the population is", population["population"])
# print(g.__next__())
# print(g.__next__())
#
# eval() 函数用来执行一个字符串表达式，并返回表达式的值
x = 7
r = eval('3 * x')
print(r)   # 21

# 生产者消费者模型, 模拟了并发
import time
def consumer(name):    # this is a generator function
    print("my name is %s,start to eat baozi" % name)
    while True:
        baozi = yield   # 看见yield,就停下，yield能保存函数状态
        time.sleep(0.1)
        print("%s 开心的吃%s包子" % (name, baozi))
def producer():
    c1 = consumer("zhangsan")    # 获得生成器
    c1.__next__()
    c2 = consumer("lisi")    # 获得生成器
    c2.__next__()              # 触发生成器运行

    for i in range(10):
        time.sleep(0.1)
        c1.send("baozi%s" % i)   # 把内容传递给baozi，也就是yield
        c2.send("baozi%s" % i)   # 把内容传递给baozi，也就是yield

producer()

# 函数传递参数，是引用
name = "a"
def show(name):
    print(id(name))
print(id(name))
show(name)

# 使用set集合获取两个列表中相同的元素

l1 = [11, 22, 33]
l2 = [22, 33, 44,'a']
l = l1 + l2
print(l)    # 连个列表拼接在一起
print(set(l))     # 用集合去掉了重复元素

print(set(l1)&set(l2))    # 用&操作，取出集合中相同的元素

