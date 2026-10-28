#!/usr/bin/env python3
# encoding=utf-8
"""
@Time    : 2026/10/27 21:27
@Author  : sam
@File    : 37-mutable-list.py
@Description: Always use None as the default placeholder for lists, dictionaries,
or sets in Python functions and class initializers. Refer to NO. 38 example.
"""


class Test(object):
    def __init__(self, test_cases=[]):
        self.test_cases = test_cases

    def add_case(self, case_id):
        self.test_cases.append(case_id)
        return self.test_cases


if __name__ == '__main__':
    run1 = Test(['a'])   # custom list
    print(run1.add_case('CAN_01'))   # ['a', 'CAN_01']

    run2 = Test()
    print(run2.add_case('CAN_02'))   # ['CAN_02']

    run3 = Test()
    print(run3.add_case('CAN_03'))   # ['CAN_02', 'CAN_03']
