class FooParent(object):
    def __init__(self, c):
        self.parent = 'I\'m the parent.'
        self.a = c
        self.b = 20
        print('Parent')

    def bar(self, message):
        print("%s from Parent" % message)


class FooChild(FooParent):
    def __init__(self, d):
        # super(FooChild,self) 首先找到 FooChild 的父类（就是类 FooParent），
        # 然后把类B的对象 FooChild 转换为类 FooParent 的对象03_面向对象/03_单继承练习.py:16
        super().__init__(d)
        print('Child')

    def bar(self, message):
        super().bar(message)
        print('Child bar function')


if __name__ == '__main__':
    fooChild = FooChild(10)
    fooChild.bar('HelloWorld')
    print(fooChild.a)
    print(fooChild.b)
