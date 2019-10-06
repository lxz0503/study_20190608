# coding=utf-8

def func(m):
    for k, v in m.items():
        m[k+2] = v + 2     # dictionary changed size during iteration


m = {1:2, 3:4}
l = m    # 这相当于浅拷贝，只是拷贝了引用，m和l都同时指向一个地址
l[9] = 10  # 给字典添加元素
# func(l)     # 函数体有问题
m[7] = 8   # 给字典添加元素
print("l is", l)
print("m is", m)
print(type(m))

# l is {1: 2, 3: 4, 9: 10, 7: 8}
# m is {1: 2, 3: 4, 9: 10, 7: 8}
# <class 'dict'>




