#!/usr/bin/env python3
# coding=utf-8

import os
import re

def gen_txt():
    log_dir = os.path.dirname(__file__) + '/test_result/'
    p = re.compile(r'<<.*-.*-\d+\.\d+: .*')
    for log_file in os.listdir(log_dir):
        if log_file == 'DHCPS.log':
            with open(log_dir + '/' +log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    r = p.match(line)
                    if r is not None:
                        yield r.group().lstrip('<<')

if __name__ == '__main__':
    r = gen_txt()
    for line in r:
        print(line)