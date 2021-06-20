import unittest
import time
class Test1(unittest.TestCase):
    def setUp(self):
        print("开始执行脚本01")
    def tearDown(self):
        time.sleep(3)
        print("脚本01执行结束！")
    def test_01(self):
        print("执行第一个用例！")
    def test_02(self):
        print("执行第二个脚本！")
    def test_03(self):
        print("执行第三个脚本！")
if __name__ == "__main__":
    unittest.main()
