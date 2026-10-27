#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:8/17/2022 10:14 AM
@file:test_shanghai.py
@project:xiaozhan_git
"""
import pytest


# class TestPudong(object):
def setup_module():
    print('setup_module')


def teardown_module():
    print('teardown_module')


def test_a():
    assert 1 == 1


def test_b():
    assert 3 == 5


def c():  # 这种不以test开头的不会执行
    assert 4 == 4


if __name__ == "__main__":
    pytest.main(['-s', 'test_pudong.py'])
