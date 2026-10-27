import unittest

from demo6_unittest_testcase import TestCase01, TestCase02

# 实例化TestSuite类
suite = unittest.TestSuite()
# 以测试用例类里的每一个方法为单位添加
# suite.addTest(TestCase01("testcase_01"))
# suite.addTest(TestCase01("testcase_02"))
# suite.addTest(TestCase02("testcase_02"))

# 以测试用例类为单位添加
suite.addTest(unittest.makeSuite(TestCase01))
suite.addTest(unittest.makeSuite(TestCase02))

runner = unittest.TextTestRunner()
runner.run(suite)

