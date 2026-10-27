#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:8/17/2022 1:29 PM
@file:test_fixture.py
@project:xiaozhan_git
"""
# http://www.51testing.com/mobile/view.php?itemid=4476374  example
import pytest


@pytest.fixture(scope='class', autouse=True)
# @pytest.fixture(scope='function', autouse=True)
# @pytest.fixture(autouse=True)
def bef():
    print('before test')


@pytest.fixture(params=[1, 2, 3])
def need_data(request):  # xiaozhan 注意需要传入request参数
    return request.param

def test_f():
    assert 2 == 2

class TestFixture(object):

    def test_a(self):  # fixture作为参数传递
        assert 1 == 1
    #
    @pytest.mark.usefixtures('bef')  # 作为装饰器传递
    def test_b(self):
        assert 3 == 5

    # 如果下面的参数没有need_data，可以设置为装饰器传递参数
    # @pytest.mark.usefixtures('need_data')
    def test_c(self, need_data):
        print('test data is %s' % need_data)
        assert need_data != 3

    #
    def c(self):  # 这种不以test开头的不会执行
        assert 4 == 4


if __name__ == "__main__":
    pytest.main()
