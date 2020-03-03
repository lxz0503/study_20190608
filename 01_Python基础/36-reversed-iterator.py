#!/usr/bin/env python3
# coding=utf-8

class FloatRange(object):
    def __init__(self, start, end, step=0.1):
        self.start = start
        self.end = end
        self.step = step
# 正向迭代
    def __iter__(self):
        t = self.start
        while t <= self.end:
            yield t
            t += self.step
# 反向迭代接口
    def __reversed__(self):
        t = self.end
        while t >= self.start:
            yield t
            t -= self.step

# test
if __name__ == '__main__':
    for x in FloatRange(1.0, 4.0, 0.5):
        print(x)
    print('反向迭代：')
    for x in reversed(FloatRange(1.0, 4.0, 0.5)):
        print(x)




