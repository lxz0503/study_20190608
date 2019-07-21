class A(object):
    def __init__(self):
        self.n = 2

    def add(self, m):
        print("this is at class A")
        self.n += m


class B(A):
    def __init__(self):
        self.n = 5

    def add(self, m):
        print('this is at class B')
        print("the initial value of self.n is %d" % self.n)
        super().add(m)  # 这里继承了父类的add方法,相当于执行了self.n += m, 跳到class A里面的add方法去执行
        print("继承父类方法add()后, self.n的值 is %d" % self.n)
        self.n += 3

b = B()
b.add(2)    # this is at class B, the initial value of self.n is 5
print(b.n)  # 输出10

