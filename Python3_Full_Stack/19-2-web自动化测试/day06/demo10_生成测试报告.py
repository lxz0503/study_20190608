import HTMLTestRunner
import unittest

# 使用suite导入测试用例
# suite = unittest.TestSuite()
# suite.addTest(unittest.makeSuite(TestCase01))

# 使用discover导入测试用例
discover = unittest.defaultTestLoader.discover("./cases", pattern='*.py')

with open("./reports/haha.html", "wb") as f:
    h = HTMLTestRunner.HTMLTestRunner(stream=f, title="测试报告", description="windows chrome")
    h.run(discover)
