#coding=utf-8
class animal:

	  #定义类的属性（动物年龄）
age =10 
#Python的初始化函数
    def __init__(self,name): 
        self.name=name
     #类的成员方法
    def eat(self): 
        print("have something")
        print(self.name)

#定义子类bird继承父类animal
class bird(animal):
    #定义子类的初始化函数
def __init__(self,name,color): 
    #这里定义的方法是如果子类中没有定义name属性那么就继承父类的name属性，如果子类中定义了name属性，那么就使用子类定义的属性。
        super(bird,self).__init__(name) 
        #定义属性color
        self.color=color
    #定义方法fly
    def fly(self):
        print(self.name)
        print(self.color)

#开始执行，有点类似java的main方法，相当于程序的主入口，可以直接在命令行执行等。
if __name__=='__main__':
a = animal("xiaoli")
a.eat()
    #实例化对象的操作。
    b =bird("xiaoniao","red") 
    b.fly()
b.eat()
#打印对象b的属性值，以字典的形式。
    print(b.__dict__)
