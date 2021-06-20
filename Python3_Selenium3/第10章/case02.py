import unittest
import time
class Test2(unittest.TestCase):
    def setUp(self):
        print("开始执行脚本02")
    def tearDown(self):
        time.sleep(3)
        print("脚本02执行结束！")
    def test_04(self):
        print("执行第4个用例！")
    def test_05(self):
        print("执行第5个脚本！")
    def test_06(self):
        print("执行第6个脚本！")
if __name__ == "__main__":
    unittest.main()
