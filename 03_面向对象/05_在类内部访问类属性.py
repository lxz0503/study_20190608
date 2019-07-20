class Dog(object):
    tricks = []

    def __init__(self, name):
        self.name = name

    # def add_trick(self, trick):
    #     self.tricks.append(trick)
    # 下面的方法等同于上面的方法。因为只访问类属性，所以可以定义一个类方法
    @classmethod
    def add_trick(cls, trick):
        cls.tricks.append(trick)

    @classmethod
    def fun(cls, trick):
        cls.add_trick(trick)

# 在实例方法内部访问类方法，也是直接用 self.类方法名
    def test(self, trick):
        self.add_trick(trick)


d = Dog('Fido')    # 创建一个实例
d.test('roll over')
print(d.tricks)    # 在类外部，实例访问类属性