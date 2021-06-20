import unittest
class add(unittest.TestCase): #声明一个测试类
    def setUp(self):
        pass
    def test_01(self):
        self.assertEqual(2,2) # test_01方法是为了判断 2 与 2是否相等，预期结果是相等
    def test_02(self):
        self.assertEqual('selenium','appium') #test_02方法是为了判断"selnium"字符串和"appium"是否相等，预期结果是不等
    def test_03(self):
        self.assertEqual('se','se')# test_03方法是为了判断"se"字符串和"se"是否同样字符串，预期结果是相等
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
