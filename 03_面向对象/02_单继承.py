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
        super().add(m)
        print('newb')
        self.n += 3

b = B()
b.add(2)
print(b.n)

