import unittest
import time
class Test1(unittest.TestCase):
    def setUp(self):
        print("开始执行脚本03")
    def tearDown(self):
        time.sleep(3)
        print("脚本03执行结束！")
    def test_07(self):
        print("执行第7个用例！")
    def test_08(self):
        print("执行第8个脚本！")
    def test_09(self):
        print("执行第9个脚本！")
if __name__ == "__main__":
    unittest.main()
