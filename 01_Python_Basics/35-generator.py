#!/usr/bin/env python3
# coding=utf-8

def f():
    print("in f(),1")
    yield 1

    print('in f(),2')
    yield 2

    print('in f(),3')
    yield 3

# example for generator

g = f()
g.__next__()    # in f(),1
g.__next__()    # in f(),2
next(g)         # in f(),3
