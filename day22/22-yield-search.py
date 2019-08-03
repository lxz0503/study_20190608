# 迭代是Python最强大的功能之一，是访问集合元素的一种方式。
# 迭代器是一个可以记住遍历的位置的对象。
# 迭代器对象从集合的第一个元素开始访问，直到所有的元素被访问完结束。
# 迭代器只能往前不会后退。
# 迭代器有两个基本的方法：iter() 和 next()。
# 字符串，列表或元组对象都可用于创建迭代器

l = [1, 2, 3, 4]
it = iter(l)    # 创建迭代器对象
# print(type(it))
# print(next(it))
# 迭代器对象可以使用常规for语句进行遍历
# for x in it:
    # print(x, end="\t")

# 在 Python 中，使用了 yield 的函数被称为生成器（generator）。
# 跟普通函数不同的是，生成器是一个返回迭代器的函数，只能用于迭代操作，
# 更简单点理解生成器就是一个迭代器。
# 在调用生成器运行的过程中，每次遇到 yield 时函数会暂停并保存当前所有的运行信息，返回 yield 的值,
# 并在下一次执行 next() 方法时从当前位置继续运行。
# 调用一个生成器函数，返回的是一个迭代器对象。

# 有一个序列，查找里面数字10的下标，用迭代器实现
def func(l):
    for i in l:
        yield i


l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
res = func(l)     # 迭代器对象
i = 0    # 全局变量记录下标
for j in res:
    if j != 10:
        i = i + 1
    else:
        print("the index of 10 is %d" % i)  # the index is 9
        break

# another method
l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
i = 0
for j in l:
    if j != 10:
        i = i + 1
    else:
        print("the index is %d" % i)
        break
# another method
l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
print("the index is %d" % l.index(10))	 # 返回列表中第一个值为 x 的元素的索引。如果没有匹配的元素就会返回一个错误

# another method
l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
for index, item in enumerate(l):
    if item == 10:
        print("10的位置是", index)
