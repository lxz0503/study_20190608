# map()它接收一个函数 f 和一个可迭代对象(这里理解成 list)，
# 并通过把函数 f 依次作用在 list 的每个元素上，得到一个新的 list 并返回
# map()函数不改变原有的 list，而是返回一个新的 list
# map() 会根据提供的函数对指定序列做映射。
# 第一个参数 function 以参数序列中的每一个元素调用 function 函数，返回包含每次 function 函数返回值的新列表

def square(x):  # 计算平方
    return x ** 2

res = map(square, [1, 2, 3, 4, 5])  # 计算列表各个元素的平方
# [1, 4, 9, 16, 25]
# TODO:use comprehensions   列表表达式
res = [x**2 for x in [1, 2, 3, 4, 5] if x > 1 and x < 5]
print(res)

# TODO:map function return an address,you must use a list to show it.
res = map(lambda x: x ** 2, filter(lambda x: x > 1 and x < 5, [1, 2, 3, 4, 5]))  # 使用 lambda 匿名函数
# [4, 9, 16]
print(list(res))

# 提供了两个列表，对相同位置的列表数据进行相加
map(lambda x, y: x + y, [1, 3, 5, 7, 9], [2, 4, 6, 8, 10])
# [3, 7, 11, 15, 19]
