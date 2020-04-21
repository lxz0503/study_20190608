#!/usr/bin/env python3
# coding=utf-8
"""This example is using pdb to debug python code."""

import pdb


def sum_nums(n):
    s = 0
    for i in range(n):
        pdb.set_trace()   # this is to set breakpoint
        s += i
        print(s)


if __name__ == '__main__':
    sum_nums(5)