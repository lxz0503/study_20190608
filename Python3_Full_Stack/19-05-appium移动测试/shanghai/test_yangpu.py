#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:8/17/2022 10:14 AM
@file:test_shanghai.py
@project:xiaozhan_git
"""
import pytest
import allure


class TestYangpu(object):
    def setup_class(self):
        print('setup_class')

    def teardown_class(self):
        print('teardown_class')

    # @pytest.mark.skipif(condition=True, reason="None")
    # @pytest.mark.skip()
    @allure.step('hhhhhhh')
    def test_a(self):
        assert 1 == 1

    # @pytest.mark.parametrize('a', [(3,6),(9,12)])   # 外面可以传入元组列表
    @pytest.mark.parametrize('a', [3,5,6])
    def test_b(self, a):
        # print('test data a0=%s' % a[0])
        # print('test data a1=%s' % a[1])
        allure.attach('这里出错 %s' % a)
        assert a % 3 == 0

    @pytest.mark.parametrize('args', [('xiaoming',18),('beijing',20)])
    def test_p(self,args):
        print(args)

    def c(self):  # 这种不以test开头的不会执行
        assert 4 == 4


if __name__ == "__main__":
    pytest.main()
