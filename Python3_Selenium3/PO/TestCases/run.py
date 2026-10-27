#!/usr/bin/env python3
# coding=utf-8
# this is the entry function, run this for all test
import unittest
import HTMLTestRunner
import time
from Common.function import projectPath   # import function name

if __name__ == '__main__':
    test_dir = projectPath() + "TestCases"
    tests = unittest.defaultTestLoader.discover(test_dir,
                                                pattern='test*.py',
                                                top_level_dir=None)
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    filepath = projectPath() + "/Reports/" + now + '.html'
    with open(filepath, 'wb') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title=u'自动化测试报告', description=u'测试报告')
        runner.run(tests)

