# 1、 _xx 以单下划线开头的表示的是protected类型的变量。即保护类型只能允许其本身与子类进行访问。
# 若内部变量标示，如： 当使用“from M import”时，不会将以一个下划线开头的对象引入 。
# 2、 __xx 双下划线的表示的是私有类型的变量。
# 只能允许这个类本身进行访问了，连子类也不可以用于命名一个类属性（类变量），
# 调用时名字被改变（在类FooBar内部，__boo变成_FooBar__boo,如self._FooBar__boo）


class Pub(object):
    # 类的私有变量和保护类型变量
    _name = 'protected类型的变量'
    __info = '私有类型的变量'

    def _func(self):
        print("这是一个protected类型的方法")

    def __func2(self):
        print('这是一个私有类型的方法')

    def get(self):   # 类里面的普通方法，用来获取私有变量
        return self.__info

a = Pub()
print(a._name)    # 'protected类型的变量'
a._func()         # 这是一个protected类型的方法"
print(a.get())
# 如果想要在实例中获取到类的私有变量，
# 可以通过在类中声明普通方法，返回私有类形变量的方式获取。
