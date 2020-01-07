#!/usr/bin/env python3
# coding=utf-8
#
from collections import deque
from random import randint
import pickle

N = randint(0, 100)

history = deque([], 5)    # [1,2,3,4,5] 如果再来一个数字6，则队列变成[2,3,4,5,6]
pickle.dump(history, open('history', 'wb'))
history = pickle.load(open('history', 'rb'))

def guess(k):
    if k ==N:
        print('right')
        return True
    if k < N:
        print('%s is less than N' % k)
    else:
        print('%s is greater than N' % k)
    return False

while True:
    line = input('please input a number:')
    if line.isdigit():
        k = int(line)
        history.append(k)
        pickle.dump(history, open('history', 'wb'))
        if guess(k):
            break
    elif line == 'history' or line == 'h?':
        print(list(history))
