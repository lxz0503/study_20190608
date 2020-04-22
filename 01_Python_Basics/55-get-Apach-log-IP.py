#!/usr/bin/env python3
# coding=utf-8
# this is to analyze apache log
# from  __future__ import print_function    # this is for running python2 version
from collections import Counter
ips = []
with open('http_code', 'r') as f:
    for line in f:
        print(line.split()[0])
        ips.append(line.split()[0])
print('PV is {0}'.format(len(ips)))
print('UV is {0}'.format(len(set(ips))))
################most visting site#####
c = Counter()
with open('http_code', 'r') as f:
    for line in f:
        c[line.split()[5]] += 1
print('PV is {0}'.format(c.most_common(2)))

####calculate error visit######
d = {}  # empty dict
with open('http_code', 'r') as f:
    for line in f:
        key = line.split()[7]
        d.setdefault(key, 0)   # default value is 0
        d[key] += 1
print(d)      # {'200': 1, '400': 2, '403': 1, '404': 1}

sum_req = 0   # total visits
err_req = 0   # error visits
print(d.items())
for key, val in d.items():
    if int(key) >= 400:
        err_req += val
    sum_req += val
print('error rate is {0:.2f}%'.format(err_req*100.0/sum_req))







