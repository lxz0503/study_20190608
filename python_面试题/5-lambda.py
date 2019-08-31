# lambda 表达式
# 参数可以有多个，用逗号隔开
# 匿名函数不管逻辑多复杂，只能写一行，且逻辑执行结束后的内容就是返回值
# 返回值和正常的函数一样可以是任意数据类型

# *args代表位置参数，它会接收任意多个参数并把这些参数作为元祖传递给函数。
# **kwargs代表的关键字参数，返回的是字典，   位置参数一定要放在关键字前面

temp = lambda x,y:x+y
print(temp(4, 10))

# 如何用一行代码生成[1, 4, 9, 16, 25, 36, 49, 64, 81, 100] ?

s = [i * i for i in range(1,11)]
print(s)

l1 = (('a'), ('b'))
l2 = (('c'), ('d'))
print(list(dict(zip(l1,l2)).items()))       # [('a', 'c'), ('b', 'd')]
print([{n[0]:n[1]} for n in zip(l1,l2)])    # [{'a': 'c'}, {'b': 'd'}]

# lambda
# 冒号前面的参数是形参，冒号后面是函数体
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
