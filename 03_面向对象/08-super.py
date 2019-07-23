class Vehicle(object):
    def __init__(self, name, speed, load, power):
        self.name = name
        self.speed = speed
        self.load = load
        self.power = power

    def run(self):
        print('starting')


class Subway(Vehicle):
    def __init__(self, name, speed, load, power, line):   # 当前有5个参数
        super().__init__(name, speed, load, power)   # 从父类继承了四个参数,子类增加一个参数
        self.line = line    # 子类新增参数初始化

    def show_info(self):
        print(self.name, self.speed, self.load, self.power, self.line)

    def run(self):
        super().run()    # 继承了父类的run()方法, 打印starting
        print("%s %s line,starting" % (self.name, self.line))


line13 = Subway('beijing subway', '10KM/h', 300, 'electricity', 13)
line13.show_info()   # beijing subway 10KM/h 300 electricity 13
line13.run()       # starting       beijing subway 13 line,starting