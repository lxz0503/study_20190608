"""iter()"""
# !/usr/bin/env python3
# coding=utf-8

import itertools

def test_func(x):
    return x < 40

def main():
    # TODO: cycle iterator can be used to cycle over a collection
    seq1 = ['a', 'b', 'c']
    cyclye1 = itertools.cycle(seq1)
    print(next(cyclye1))   # a
    print(next(cyclye1))   # b
    print(next(cyclye1))   # c
    print(next(cyclye1))   # a
    # TODO: use count to create a simple counter
    count1 = itertools.count(100, 10)
    print(next(count1))   # 100
    print(next(count1))   # 110
    # TODO: use accumulate
    vals = [10, 20, 30, 40, 50, 50]
    acc = itertools.accumulate(vals, max)   # until the max number
    print(list(acc))
    # TODO: use chain to connect sequence together
    # x = itertools.chain('ABCD', 'aaaa')
    x = itertools.chain(['a', 'b', 'c'], 'aaaa')
    print(list(x))
    # TODO: dropwhile and takewhile will return values until
    # a certain condition is met that stops them
    print(list(itertools.dropwhile(test_func, vals)))   # [40, 50, 50]
    print(list(itertools.takewhile(test_func, vals)))   # [10, 20, 30]


if __name__ == '__main__':
    main()