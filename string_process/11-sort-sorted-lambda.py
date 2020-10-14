# 今天来讲一下Python中的排序函数。Python中有2个内建的排序函数，分别为sort() 和 sorted()

# 下面介绍分别介绍一下2个函数：

# 1.有一个列表 ：a=[1,4,5,88,0,7]，想要实现排序功能，可以使用sort() 和 sorted()；
a=[1,4,5,88,0,7]
a.sort()              # 默认升序排列
print(a)              #输出：[0, 1, 4, 5, 7, 88]

a.sort(reverse=True)  # reverse=True，降序排列。默认FALSE：升序；
print(a)              # 输出：[88, 7, 5, 4, 1, 0]

b = sorted(a,reverse=True)   #有返回值，需要用一个变量进行接收
print(b)              # 输出：[88, 7, 5, 4, 1, 0]

# 在这里，可以看出sort()是没有返回值的，它会改变原有的列表，而sorted()需要用一个变量进行接收，它并不会修改原有的列表

# 2. 参数key的应用：
# 什么情况下使用：当列表中的元素不再单一，若列表中包含元组或字典
# 如何应用：     使用lambda代表根据什么元素或key值进行排序
# 列表中包含元组，通过元组中某个元素进行排序；lambda x:x[元素位置]
stu = [("winnie", "A", 12),("lucy", "C", 16),("john", "B", 14)]
stu.sort(key=lambda x: x[2])
print(stu)
s = sorted(stu, key=lambda x: x[1], reverse=True)  # 默认false ,升序
print(s)
# 输出：
# [('winnie', 'A', 12), ('john', 'B', 14), ('lucy', 'C', 16)]
# [('lucy', 'C', 16), ('john', 'B', 14), ('winnie', 'A', 12)]
# 列表中包含字典，按照字典中某个key值进行排序  lambda x:x[key值]
l1 = [{'name0': '李丽', 'age': 40}, {'name0': '张那', 'age': 30},{'name0':'王原','age':50},{'name0':'王丽萍','age':50}]
l2 = sorted(l1, key=lambda x:x['age'])
print(l2)
# 结果：[{'name0': '张那', 'age': 30}, {'name0': '李丽', 'age': 40}, {'name0': '王原', 'age': 50}, {'name0': '王丽萍', 'age': 50}]

# 3.什么情况下不能使用sort()函数？
# sort()函数是list的内建函数，不能针对字典等迭代，系统会直接报错  AttributeError: 'dict' object has no attribute 'sort'

# 4.sorted()函数使用举例：
# 有一个字典如下所示：
# 其中key表示数字，value表示这个数字出现的次数，比如1:2表示数字1出现了2次。
# 请针对这个字典按照出现的次数从多到少进行排序。

dict1={1: 2, 2: 2, 3: 1, 4: 7, 5: 6, 6: 4, 7: 3, 8: 2, 9: 1}

d1=sorted(dict1.values(),reverse=True)    #按values值进行排序
d2=sorted(dict1)                      #
d3=sorted(dict1.keys(),reverse=True)  #按key值进行排序
print(d1)
print(d2)
print(d3)

# 输出：
# [7, 6, 4, 3, 2, 2, 2, 1, 1]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
# [9, 8, 7, 6, 5, 4, 3, 2, 1]
# lambda函数添加一个参数
foo = [['z',19],['ll',54],['wa',23],['df',23],['xf',23]]
a = sorted(foo, key=lambda x: (x[1], x[0]))  # 先按照x[1]排序，然后对于x[1]相同的，按照x[0]排序
print(a)    # [['z', 19], ['df', 23], ['wa', 23], ['xf', 23], ['ll', 54]]

# 根据键对字典排序    zip 函数
dic = {'name':'za', 'sex':'man', 'city':'bj'}
foo = zip(dic.keys(), dic.values())
foo = [i for i in foo]
print('字典转换成列表嵌套元组', foo)
b = sorted(foo, key=lambda x:x[0])
print('根据键排序', b)
# 字典推导式构造新字典
new_dic = {i[0]:i[1] for i in b}
print(new_dic)
# 字典转换成列表嵌套元组的更简单的方法如下
dic = {'name':'za', 'sex':'man', 'city':'bj'}
foo = list(dic.items())
print('字典转换成列表嵌套元组', foo)

# 列表推导式，字典推导式，生成器
import random
td_list = [i for i in range(10)]    # 0-9
dic = {k: random.randint(4, 9) for k in ['a','b','c','d']}    # 4-8 not include 9
print(dic)     # {'a': 6, 'b': 5, 'c': 4, 'd': 8}
# 统计字符串中某个字符出现的次数
s = "beijing shang beijing tianjin a b"
a = s.count('beijing')
print(a)