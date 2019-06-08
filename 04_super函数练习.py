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


class Son(Man, Woman):
    def __init__(self):
        print("我是儿子我要好好学习")

    def study(self):
        print("我要学好化学和物理")
        super().study()

son1 = Son()
print(Son.mro())
print(Man.mro())
son1.study()