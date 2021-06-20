import unittest
import time
class Test1(unittest.TestCase):
    def setUp(self):
        print("开始执行脚本04")
    def tearDown(self):
        time.sleep(3)
        print("脚本04执行结束！")
    def test_10(self):
        print("执行第10个用例！")
    def test_11(self):
        print("执行第11个脚本！")
    def test_12(self):
        print("执行第12个脚本！")
if __name__ == "__main__":
    unittest.main()
