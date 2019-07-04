"""
zip() 函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的列表。

如果各个迭代器的元素个数不一致，则返回列表长度与最短的对象相同，利用 * 号操作符，可以将元组解压为列表
在 Python 3.x 中为了减少内存，zip() 返回的是一个对象。如需展示列表，需手动 list() 转换。
"""

a = [1, 2, 3]
b = ["xiaozhan", "beijing", "shanghai"]
c = [4, 5, 6, 7, 8]
zipped = zip(a, b)     # 打包为元组的列表
print(list(zipped))
for item in zipped:
    print(item)
# [(1, 'xiaozhan'), (2, 'beijing'), (3, 'shanghai')]
           # 元素个数与最短的列表一致
l = [(1,2), (3,4),(5,6)]
print(max(l))
