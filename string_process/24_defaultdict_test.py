"""this is for defaultdict"""
# !/usr/bin/env python3
# coding=utf-8
from collections import defaultdict


def main():
    # define a list of items that we want to count
    fruits = ['apple', 'pear', 'orange', 'banana', 'apple', 'orange', 'grape', 'banana']
    # TODO: use defaultdict to count each element
    fruit_counter = defaultdict(int)
    # count the element in the list
    for fruit in fruits:
        fruit_counter[fruit] += 1
    # print the result
    for (k, v) in fruit_counter.items():
        print(k + ':' + str(v))


if __name__ == '__main__':
    main()