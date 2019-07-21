# 下面的例子是介绍类属性的使用
class Tool(object):
   # 使用赋值语句定义类属性，记录所有工具对象的属性
    count = 0

    def __init__(self, name):
        self.name=name
        # 类类属性+1
        Tool.count += 1   # 每调用一次，类属性的值就+1


# 类定义结束,开始使用类
tool1 = Tool("刀")         # 每定义一个实例对象，类属性的值就+1
tool2 = Tool("剑")
tool3 = Tool("火")
tool4 = Tool("箭")
tool1.count = 100        # 只是给tool1这个实例增加了一个实例属性，不会改变类属性
print(tool1.__dict__)   # {'name': '刀', 'count': 100}
print("tool2的实例属性", tool2.__dict__)   # tool2的实例属性 {'name': '剑'}
# 使用赋值语句，类对象.类属性不会修改类属性的值
print(tool1.count)     # 输出100
print("%d" % Tool.count)     # 输出4
