import ddt
import unittest

@ddt.ddt
class test_se(unittest.TestCase):
    def setUp(self):
        pass

    @ddt.file_data("tt.json") #文件 tt.json 放在当前文件夹内。
    def test_01(self,tt):
        print(tt)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
