# polymorphic美 [ˌpɑˌliˈmɔrfɪk]   多态
# 多态性是指 具有不同功能的函数可以使用相同的函数名，这样就可以用一个函数名调用不同内容的函数
# 在面向对象方法中一般是这样表述多态性：向不同的对象发送同一条消息，不同的对象在接收时会产生不同的行为（即方法）。
# 也就是说，每个对象可以用自己的方式去响应共同的消息。
# 所谓消息，就是调用函数，不同的行为就是指不同的实现，即执行不同的函数。
# 多态性依赖于：继承    有了继承，才能有多态
# 多态性：定义统一的接口

class Animal(object):
    def run(self):
        raise AttributeError('子类必须实现这个方法')


class People(Animal):
    def run(self):
        print('人正在走')


class Pig(Animal):
    def run(self):
        print('pig is walking')


class Dog(Animal):
    def run(self):
        print('dog is running')

# 多态的体现，都是调用run()函数
peo1 = People()
pig1 = Pig()
d1 = Dog()

peo1.run()
pig1.run()
d1.run()

# 下面和上面的实现类似，都是多态的体现
# 多态性：一种调用方式，不同的执行效果（多态性）
def func(obj):
    obj.run()

func(peo1)
func(pig1)
func(d1)



