#!/usr/bin/env python3
# coding=utf-8
# 素数是指质数，一个大于1的自然数，除了1和它自身外，不能整除其他自然数的数叫做质数；否则称为合数
class PrimeNumbers(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def is_prime(self, k):
        if k < 2:
            return False
        for i in range(2, k):
            if k % i == 0:
                return False
        # for 循环结束，表明是素数
        return True

    # 迭代器接口
    def __iter__(self):
        for k in range(self.start, self.end + 1):
            if self.is_prime(k):
                yield k
# test
if __name__ == '__main__':
    for x in PrimeNumbers(1, 100):
        print(x)


