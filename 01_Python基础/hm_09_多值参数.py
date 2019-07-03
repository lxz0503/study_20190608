# python有两种多值参数
# 参数名前增加一个*,可以接收元组
# 参数名前增加两个*,可以接收字典


def demo(num, *args, **kwargs):
    print(num)
    print(args)
    print(kwargs)


demo(1, 2, 3, 4, 5, name="xiaoming", age=18, gender=True)