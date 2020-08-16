"""this is for namedtuple"""
# https://www.jianshu.com/p/47f66ff4ab7b  --- this is for collections module, a little difficult to understand
# !/usr/bin/env python3
# coding=utf-8
from collections import namedtuple
import csv


def small_examples():
    # TODO: create a namedtuple which is for small programs
    # Animal = namedtuple('Animal', 'name age type')    # one para is tuple name, another is filed name which is a sequence
    # Animal = namedtuple('Animal', ['name', 'age', 'type'])
    Animal = namedtuple('Animal', ('name', 'age', 'type'))   # define a namedtuple
    # perry = Animal(name='perry', age=30, type='cat')    # initialize  tuple
    # perry = Animal(*['perry', 30, 'cat'])    # initialize namedtuple with a list
    # perry = Animal(*('perry', 30, 'cat'))    # initialize namedtuple with a tuple
    perry = Animal(*{'perry', 30, 'cat'})      # initialize namedtuple with a set
    print(perry.name, perry.age, perry.type)
    # print(perry[0], perry[1], perry[2])
    # TODO: use _replace to create a new instance
    perry = perry._replace(age=40)
    print(perry)


def get_data(file_name):  # real project, read data from csv file
    with open(file_name) as f:
        f_csv = csv.reader(f)
        headings = next(f_csv)  # use next() to get the first line--headings is a list
        Row = namedtuple('Row', headings)  # define a namedtuple with headings(a list)
        for r in f_csv:
            # print(r)
            yield Row(*r)    # generator, to initialize the namedtuple---Row. *r means r is a sequence(iterable)


def show_namedtuple():
    for i, t in enumerate(get_data('data.csv'), 1):      # the table index always starts from 1
        args = [(i, t.name, t.status, t.arch, t.sprint)]      # this is to generate parameter for excecutemany
        print(args)


if __name__ == '__main__':
    small_examples()
    # show_namedtuple()
