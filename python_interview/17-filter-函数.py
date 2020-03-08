# filter() 函数用于过滤序列，过滤掉不符合条件的元素，返回一个迭代器对象，
# 如果要转换为列表，可以使用 list() 来转换。
#
# 该接收两个参数，第一个为函数，第二个为可迭对象，
# 序列的每个元素作为参数传递给函数进行判，然后返回 True 或 False，最后将返回 True 的元素放到新列表中

def is_odd(n):
    return n % 2 == 1


tmplist = filter(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
newlist = list(tmplist)
print(newlist)              # [1, 3, 5, 7, 9]


# 使用filter，lambda,用于去除列表中所有某个特定的元素
nums = [0, 1, 2, 2, 3, 0, 4, 2]
f = filter(lambda n: n != 2, nums)
L = list(f)
print(L)