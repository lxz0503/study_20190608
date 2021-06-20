#coding=utf-8
class Person(object):
    def __init__(self,name,age):
        self.name = name
        self.age = age

    def print_info(self):
        print('%s: %s' % (self.name,self.age))


p1 = Person('Jack',23)
print(p1.name)
print(p1.age)
