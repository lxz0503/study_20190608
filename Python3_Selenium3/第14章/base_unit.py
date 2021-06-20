###
###配套视频已出版，学习有疑问联系作者qq:2574674466###
###

#coding=utf-8
import unittest
class ParaCase(unittest.TestCase):
   #unittest增加参数化
    def __init__(self, methodName='Tests', param=None):
        super(ParaCase, self).__init__(methodName)
        self.driver = param
    def setUp(self):
        self.driver.maximize_window()

@staticmethod
#以下方法是为了创建测试套件，此套件可以在被继承子类调用并在子类中设置需要运行的方法，只需要通过param参数。
    def parametrize(testcase, param=None):
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase(name, param=param))
        return suite
