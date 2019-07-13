class A(object):
    def __init__(self):
        self.n = 2

    def add(self, m):
        print('self is {0} @A.add'.format(self))
        self.n += m


class B(A):
    def __init__(self):
        self.n = 5

    def add(self, m):
        print('self is {0} @B.add'.format(self))
        #
        print("self.n is %d" % self.n)
        super().add(m)  # 这里继承了父类的add方法,相当于执行了self.n += m
        print("after running parent, the self.n is %d" % self.n)
        print('newb')
        self.n += 3

b = B()
b.add(2)    # newb
print(b.n)  # 输出10

