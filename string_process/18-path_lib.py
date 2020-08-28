#!/usr/bin/env python3
# coding=utf-8

import pathlib

script_name = pathlib.PurePosixPath('/a/b/set.py').name
print(script_name)       # set.py
suffix_name = pathlib.PurePosixPath('/a/b/set.py').suffix
print(suffix_name)    # .py
p = pathlib.PurePosixPath('/a').joinpath('b').joinpath('c')
print(p)     # /a/b/c
p = pathlib.Path.cwd()
print(p)   # it is same as os.getcwd()
p = pathlib.Path.home()
print(p)
p = pathlib.Path('a.txt')
print(p)
