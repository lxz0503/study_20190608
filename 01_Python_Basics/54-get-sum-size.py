#!/usr/bin/env python3
# coding=utf-8
# this is to calculate the size of all files

import os
logs = [item for item in os.listdir('.') if item.endswith('.py')]
sum_size = sum(os.path.getsize(os.path.join(os.getcwd(), item)) for item in logs)
print(sum_size)

s = 'it is in beijing in at in aa'
