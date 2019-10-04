# coding=utf-8
lst = [1, 2, 3]
for i in iter(lst):    # iter() creates an iterator
    print(i)

# list、tuple等都是可迭代对象，我们可以通过iter()函数获取这些可迭代对象的迭代器。
# 然后我们可以对获取到的迭代器不断使⽤next()函数来获取下⼀条数据
li = [11, 22, 33, 44, 55]
li_iter = iter(li)
print("get data from iterator", next(li_iter))
print("get data from iterator", next(li_iter))

# 在Python中，这种一边循环一边计算的机制，称为生成器：generator
# python中生成器是迭代器的一种，使用yield返回值函数，每次调用yield会暂停，而可以使用next()函数和send()函数恢复生成器
# 生成器一次只能产生一个值，这样消耗的内存数量将大大减小

# 可以直接作用于for循环的数据类型有以下几种：
# 一类是集合数据类型，如list,tuple,dict,set,str等
# 一类是generator，包括生成器和带yield的generator function
# 这些可以直接作用于for 循环的对象统称为可迭代对象：Iterable

# 一个实现了iter方法的对象是可迭代的，一个实现next方法并且是可迭代的对象是迭代器。
# 可以被next()函数调用并不断返回下一个值的对象称为迭代器：Iterator。

# print(isinstance(s,Iterator))     #判断是不是迭代器
# print(isinstance(s,Iterable))       #判断是不是可迭代对象