#!/usr/bin/env python3
# coding=utf-8
# 模拟成绩录入系统，一个人答完题，就记录时间，录入系统
# 形成一个有序的字典

from time import time
from collections import OrderedDict
from random import randint

players = list('ABCDEFGH')   # 代表8个学生
start = time()
d = OrderedDict()         # 有序字典
for i in range(8):
    input()           # a player has finished game
    p = players.pop(randint(0, 7-i))  # pop(self,index=None),每弹出一个元素，列表长度就减一
    end = time()
    print(i+1, p, end-start)
    d[p] = (i+1, end-start)