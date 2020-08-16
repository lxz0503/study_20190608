"""this is for deque"""
# !/usr/bin/env python3
# coding=utf-8
# https://www.php.cn/python-tutorials-358240.html  --refer to this link, deque is pronounced as deck
# deque is liked double ended queues
from collections import deque
import string

def main():
    # TODO: initialize a deque with lowercase letters
    d = deque(string.ascii_lowercase)  # 26 lowercase letters from a to z
    # TODO: deque supports the len() function
    print(len(d), d)
    # TODO: deque can be iterated over
    for elem in d:
        print(elem.upper(), end=' ')
    print()
    # TODO: manipulate items from either end
    d.pop()       # remove the right item
    d.popleft()   # remove the left item
    d.append(2)   # add 2 to the right side, equals d.extend(2)
    d.appendleft(1)  # add 1 to the left side, equals d.extendleft(1)
    print(d)
    # TODO: rotate the deque
    d.rotate(2)
    print(d)
    d.reverse()
    print(d)
    # TODO: index
    print(d.index('f'))
    # TODO: count, how many times it occurs
    print(d.count('d'))
    # TODO: remove element
    d.remove('x')
    print(d)


if __name__ == '__main__':
    main()