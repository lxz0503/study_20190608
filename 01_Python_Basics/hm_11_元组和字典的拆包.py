<<<<<<< HEAD
# 在调用带有多值参数的函数时，如果希望：（1）将一个元组变量传递给args（2）将一个字典变量传递给kwargs。
# 就可以选择拆包，简化参数的传递，拆包的方式是：
# 在元组变量前加一个星号*
# 在字典变量前增加两个星号**

def demo(*args, **kwargs):
    print(args)     # (1, 2, 3)
    print(kwargs)   # {'name': '小明', 'age': 18}


if __name__ == '__main__':
    gl_nums = [1, 2, 3]        # gl_nums = (1, 2, 3)
    gl_dict = {"name": "小明", "age": 18}
    demo(*gl_nums, **gl_dict)     # 如果传递的参数是可迭代序列，在前面加上*， 如果传递的是字典格式参数，则添加两个**
    # https://www.jianshu.com/p/26fed6b283f7
    # 元组拆包也叫可迭代元素拆包
    # 用 * 运算符把一个可迭代对象拆开作为函数的参数
    # 用*来处理剩下的元素在 Python 中，函数用 *args 来获取不确定数量的参数
    # 字典的拆包
    a,b = {'汪峰':'北京北京','王菲':'天后'}
    print(a,b)
    # 结果:
    # 汪峰 王菲
=======
# python 里面列表前面加星号
# 作用是将列表解开成多个独立的参数，传入函数，还有类似的有两个星号，是将字典解开成独立的元素作为形参


def demo(*args, **kwargs):
    print(args)     # (1, 2, 3)
    print(kwargs)   # {'name': '小明', 'age': 18}


if __name__ == '__main__':
    gl_nums = [1, 2, 3]        # gl_nums = (1, 2, 3)
    gl_dict = {"name": "小明", "age": 18}
    demo(*gl_nums, **gl_dict)     # 如果传递的参数是序列，在前面加上*， 如果传递的是字典格式参数，则添加两个**
>>>>>>> 47c37798140883b8d6dc21ec5da5bc7a20988ce9
