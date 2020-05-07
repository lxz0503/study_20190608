#!/usr/bin/env python3
# coding=utf-8
# this is to backup files with zip
# or you can use below simple method to generate zip file:
# python -m zipfile -c monty.zip spam.txt eggs.txt
# python -m zipfile -e monty.zip target-dir/
# python -m zipfile -1 monty.zip

import os
import fnmatch
import zipfile
import datetime


def is_file_match(filename, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def find_specific_files(root, patterns=['*'], exclude_dirs=[]):
    for root, dirnames, filenames in os.walk(root):
        for d in exclude_dirs:
            if d in dirnames:
                dirnames.remove(d)

        for filename in filenames:
            if is_file_match(filename, patterns):
                yield os.path.join(root, filename)


def main():
    patterns = ['*.jpg', '*.jpeg', '*.png', '*.tif']
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    filename = 'all_images_{0}.zip'.format(now)
    with zipfile.ZipFile(filename, 'w') as f:
        for item in find_specific_files('.', patterns):
            f.write(item)


if __name__ == '__main__':
    main()


