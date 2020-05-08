#!/usr/bin/env python3
# coding=utf-8

import os
import sys

def chmod_read(filename):
    if not os.path.isfile(filename):
        raise SystemExit(filename + ' does not exists')
    elif not os.access(filename, os.R_OK):
        os.chmod(filename, 0x777)
    else:
        with open(filename) as f:
            print(f.read())

def all_files():
    r = [item for item in os.listdir('.') if item.endswith('.txt')]
    print(r)

if __name__ == '__main__':
    chmod_read('58-read-chmod-file.py')
    all_files()