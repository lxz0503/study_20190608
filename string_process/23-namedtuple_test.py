"""this is for namedtuple"""
# !/usr/bin/env python3
# coding=utf-8
from collections import namedtuple

# TODO: create a namedtuple which is for small programs
# Animal = namedtuple('Animal', 'name age type')    # one para is tuplename, another is filed name which is a sequence
# Animal = namedtuple('Animal', ['name', 'age', 'type'])
Animal = namedtuple('Animal', ('name', 'age', 'type'))
perry = Animal(name='perry', age=30, type='cat')    # initialize  tuple
print(perry.name, perry.age, perry.type)
print(perry[0], perry[1], perry[2])
# TODO: use _replace to create a new instance
perry = perry._replace(age=40)
print(perry)