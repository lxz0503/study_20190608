#!/usr/bin/env python3
# coding=utf-8

from time import time
from collections import OrderedDict
from random import randint

players = list('abcdefgh')
start = time()
d = OrderedDict()
for i in range(8):
    input()  # a player has finished game
    p = players.pop(randint(0, 7-i))  # pop(self,index=None),每弹出一个元素，列表长度就减一
    end = time()
    print(i+1, p, end-start)
    d[p] = (i+1, end-start)