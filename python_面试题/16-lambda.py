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