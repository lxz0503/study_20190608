# python 里面列表前面加星号
# 作用是将列表解开成多个独立的参数，传入函数，还有类似的有两个星号，是将字典解开成独立的元素作为形参


def demo(*args, **kwargs):
    print(args)     # (1, 2, 3)
    print(kwargs)   # {'name': '小明', 'age': 18}


if __name__ == '__main__':
    gl_nums = [1, 2, 3]        # gl_nums = (1, 2, 3)
    gl_dict = {"name": "小明", "age": 18}
    demo(*gl_nums, **gl_dict)     # 如果传递的参数是序列，在前面加上*， 如果传递的是字典格式参数，则添加两个**
