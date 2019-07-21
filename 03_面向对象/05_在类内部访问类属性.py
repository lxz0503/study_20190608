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
    # 在类方法里面访问其它类方法,可以用  cls.类方法名
    @classmethod
    def fun(cls, trick):
        cls.add_trick(trick)
# 在其它方法内部访问类方法，也是直接用 self.类方法名
    def test(self, trick):
        self.add_trick(trick)


# 在类外面访问类
d = Dog('Fido')    # 创建一个实例
d.test('roll over')
print(d.tricks)    # 在类外部，实例访问类属性  ['roll over']
# 增加，修改，删除类属性
Dog.tricks = "aaaa"
d1 = Dog('Fido')
print(d.tricks)     # aaaa

# 增加一个类属性
Dog.age = 10
d2 = Dog('Fido')
print(d2.age)       # 10

# 删除一个类属性
del Dog.age

# 增加一个实例属性
d2.address = "beijing"
print(d2.address)
# 打印一个对象的所有实例属性
print(d2.__dict__)   # {'name': 'Fido', 'address': 'beijing'}

