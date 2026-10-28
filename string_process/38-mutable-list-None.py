#!/usr/bin/env python3
# encoding=utf-8
"""
@Time    : 2026/10/27 22:13
@Author  : sam
@File    : 38-mutable-list-None.py
@Description: Always use None as the default placeholder for lists, dictionaries,
or sets in Python functions and class initializers.
"""


class Test(object):
    def __init__(self, test_cases=None):
        # If there is custom list or not
        self.test_cases = test_cases or []

    def add_case(self, case_id):
        self.test_cases.append(case_id)
        return self.test_cases


if __name__ == '__main__':
    run1 = Test(['a'])   # with custom list
    print(run1.add_case('CAN_01'))   # ['a', 'CAN_01']

    run2 = Test()   # without custom list
    print(run2.add_case('CAN_02'))   # ['CAN_02']

    run3 = Test()   # without custom list
    print(run3.add_case('CAN_03'))   # ['CAN_03']
