# https://www.cnblogs.com/mxh1099/p/8512552.html
# #方法                                  #描述
# -------------------------------------------------------------------------------------------------
# D.clear()                              #移除D中的所有项
# D.copy()                               #返回D的副本
# D.fromkeys(seq[,val])                  #返回从seq中获得的键和被设置为val的值的字典。可做类方法调用,返回一个新的字典
# D.get(key[,default])                   #如果D[key]存在，将其返回；否则返回给定的默认值None
# D.has_key(key)                         #检查D是否有给定键key
# D.items()                              #返回表示D项的(键，值)对列表
# D.iteritems()                          #从D.items()返回的(键，值)对中返回一个可迭代的对象
# D.iterkeys()                           #从D的键中返回一个可迭代对象
# D.itervalues()                         #从D的值中返回一个可迭代对象
# D.keys()                               #返回D键的列表, 在python3里面返回dict_keys，是一个class,需要转化为list
# D.pop(key[,d])                         #移除并且返回对应给定键key或给定的默认值D的值
# D.popitem()                            #从D中移除任意一项，并将其作为(键，值)对返回
# D.setdefault(key[,default])            #如果D[key]存在则将其返回；否则返回默认值None
# D.update(other)                        #将other中的每一项加入到D中。
# D.values()                             #返回D中值的列表
# 创建字典的五种方法
# 方法一: 常规方法
# 如果事先能拼出整个字典，则此方法比较方便
D1 = {'name': 'Bob', 'age': 40}
# 方法二：动态创建
# 如果需要动态地建立字典的一个字段，则此方法比较方便
D2 = {}
D2['name'] = 'Bob'
D2['age'] = 40
print('keys', list(D2.keys())[0])
# 方法三:  dict--关键字形式f
# 代码比较少，但键必须为字符串型。常用于函数赋值
D3 = dict(name='Bob', age=45)
# 方法四: dict--键值序列,下面三种方式都可以
# 如果需要将键值逐步建成序列，则此方式比较有用,常与zip函数一起使用
D4 = dict([('name', 'Bob'), ('age', 40)])   # dict函数的参数是一个列表，列表里面的元素是键值对组成的元组
D = dict(zip(['name', 'bob'], ['age', 40]))   # zip函数里面的参数是两个列表
D = dict(zip(('name', 'bob'), ('age', 40)))   # zip函数里面的参数是两个元组
print(D)

# 字典遍历
xiaoming_dict = {"name": "小明",
                 "qq": "123456",
                 "phone": "10086"}
for k in xiaoming_dict:
    print("%s - %s" % (k, xiaoming_dict[k]))

for k in xiaoming_dict.values():      # 只取对应的value值
    print(k)

# 下面可以获取键值对，存放在元组
# ('name', '小明')
# ('qq', '123456')
# ('phone', '10086')
for k in xiaoming_dict.items():
    print(k)

# TODO:filter a dictionary
D = {'beijing': 100, 'shanghai': 90, 'tianjin': 80, 'chongqing': 70, 'nanjing': 60}
r = {k: v for k, v in D.items() if v >= 60}   # 字典解析
print(r)           # {'beijing': 100, 'shanghai': 90, 'tianjin': 80, 'chongqing': 70, 'nanjing': 60}

# randint(1,10)----生成随机数字1到10之间，包含1和10
# range(1,15)---从1开始直到14
import random
d = {x: random.randint(1, 10) for x in range(1, 15)}
print(d)
# TODO: combine 2 different dictionaries with comprehension, 字典表达式
tem1 = {'a': 1, 'b': 2, 'c': 3}
tem2 = {'d': 1, 'e': 2, 'f': 3}
res = {k: v for team in (tem1, tem2) for k, v in team.items()}
print(res)
# TODO:交换现有字典中各键值对的键和值
res1 = {v: k for k, v in tem1.items()}
print(res1)
# TODO:
team = ['beijing', 'shanghai', 'tianjin']
res = {k: len(k) for k in team}
print(res)

