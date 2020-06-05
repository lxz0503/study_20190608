#!/usr/bin/env python3
# coding=utf-8
# this is to compare 2 files, generate result into a html file.

import difflib


def readfile(filename):
    with open(filename) as fp:
        text = fp.readlines()
    return text


def compare(file1, file2, result_html):
    file1_content = readfile(file1)
    file2_content = readfile(file2)
    diff = difflib.HtmlDiff()
    result = diff.make_file(file1_content, file2_content)
    with open(result_html, 'w') as fp:
        fp.write(result)


if __name__ == '__main__':
    compare('test_result_stand.log', 'test_result0604.log', 'diff_result.html')
