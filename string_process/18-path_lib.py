#!/usr/bin/env python3
# coding=utf-8

import pathlib

script_name = pathlib.PurePosixPath('/a/b/set.py').name
print(script_name)
suffix_name = pathlib.PurePosixPath('/a/b/set.py').suffix
print(suffix_name)
p = pathlib.PurePosixPath('/a').joinpath('b').joinpath('c')
print(p)
p = pathlib.Path.cwd()
print(p)
p = pathlib.Path.home()
print(p)
p = pathlib.Path('a.txt')
print(p)
