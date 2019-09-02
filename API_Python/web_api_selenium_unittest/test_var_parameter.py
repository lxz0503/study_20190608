class Test(object):
    def __init__(self):
        self.a = (2, 5)

    def __add(self, x, y):
        return x+y

    def add(self):
        return self.__add(*self.a)


if __name__ == '__main__':
    cc = Test()
    result = cc.add()
    print(result)