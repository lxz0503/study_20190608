class Person(object):
    def __init__(self):
        print("我要好好学习")

    def study(self):
        print("我要学好语言")


class Man(Person):
    def __init__(self):
        print("我是男人我要好好学习")

    def study(self):
        print("我要学好数学")
        super().study()


class Woman(Person):
    def __init__(self):
        print("我是女人我要好好学习")

    def study(self):
        print("我要学好英语")
        super().study()


class Son(Man, Woman):     # 多重继承
    def __init__(self):
        print("我是儿子我要好好学习")

    def study(self):
        print("我要学好化学和物理")
        super().study()

son1 = Son()
# print(Son.mro())
# print(Man.mro())
son1.study()   # 注意下面的调用顺序
# 我是儿子我要好好学习          首先是 __init__函数里面的内容
# 我要学好化学和物理           调用自己函数内容，即print("我要学好化学和物理")
# 我要学好数学                第一个父类里面的函数  print("我要学好数学")
# 我要学好英语                第二个父类里面的函数  print("我要学好英语")
# 我要学好语言                最后调用顶层父类里面的方法   print("我要学好语言")