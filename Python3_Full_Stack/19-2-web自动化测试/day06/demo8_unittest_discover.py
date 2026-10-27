import unittest

# test_dir为要指定的目录 ./为当前目录；pattern：为查找的.py文件的格式
discover = unittest.defaultTestLoader.discover("./cases", pattern='*.py')

runner = unittest.TextTestRunner()
runner.run(discover)
