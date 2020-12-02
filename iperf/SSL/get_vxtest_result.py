#!/usr/bin/env python3
# coding: utf-8

import sys
import argparse
import re

dict_data = {}

def get_vxTest_result(log):
    patt_pass = re.compile(r'PASSES=1')
    patt_fail = re.compile(r'FAILS=1')
    patt_name = re.compile(r'caseName\s+:\s+(\w+)')
    with open(log, 'r', encoding='utf-8') as f:
        for line in f:
            if re.search(patt_pass, line) is not None:
                dict_data.setdefault('result',0)
            elif re.search(patt_fail, line) is not None:
                dict_data.setdefault('result',1)
            elif re.search(patt_name, line) is not None:
                dict_data.setdefault('caseName',re.search(patt_name, line).group(1))


if __name__ == '__main__':

    parse = argparse.ArgumentParser()
    parse.add_argument('-f', '--file', help='log file to process', dest='filename', required=True)
    args = parse.parse_args()
  
    log = args.filename
    get_vxTest_result(log)
    print(dict_data)
