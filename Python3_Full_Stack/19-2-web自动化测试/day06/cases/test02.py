import unittest


class TestCase02(unittest.TestCase):
    # 方法名必须以test开头
    def testcase_01(self):
        print("TestCase02_testcase_01")

    def testcase_02(self):
        print("TestCase02_testcase_02")
        self.assertEqual('heo', "hello world")

    def testcase_03(self):
        print("TestCase02_testcase_03")
