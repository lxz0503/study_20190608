#coding=utf-8
#第一种创建集合的方式：直接赋值。
set_1 = {'a','b','c','d','e'}
print("打印集合set_1:")
for s in set_1:
    print(s)
#第二种创建集合的方式：用set方法。
set_2 = set('world')
print("打印集合set_2:")
for s in set_2:
    print(s)


#coding=utf-8
#该示例代码主要是判断一个集合是否是另外一个集合的子集。
#可以用> <符号，或者用 issubset()方法进行判定。
set_1 = set('what')
set_2 = set('whatabout')
set_3 = set('whataboutyou')

print(set_1 < set_2) #应该返回 True.
print(set_2 < set_3) #应该返回 True.
print(set_3 > set_1) #应该返回 True.
print(set_1.issubset(set_2)) #结果应该返回True.



#coding=utf-8
print("以下为集合并集的操作：")
set_1 = set('what')
set_2 = set('whatabout')
set_3 = set('whataboutyou')
#set_a = set_1 | set_2  #第一种并集的方法
set_a = set_1.union(set_2)  #第二种并集的方法
for s in set_a:
    print(s)
print("以下为集合交集的操作：")
set_b = set_1 & set_2 #这是第一种交集的方式
set_b = set_1.intersection(set_2)  #这是第二种交集的方式

#打印出交集的集合元素
for s in set_b:
    print(s)

print("以下为集合差集的操作：")
set_c = set_1 - set_2 #第一种差集的方式
set_c = set_1.difference(set_2) #第二种差集的方式

#打印出差集的集合元素
for s in set_c:
    print(s)


