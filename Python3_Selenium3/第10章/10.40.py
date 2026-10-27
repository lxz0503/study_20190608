# encoding = utf-8
import unittest
import HTMLTestRunner
from selenium import webdriver
import time
import math

# 声明一个测试类
class SuiteTest1(unittest.TestCase):  # 声明一个测试类
    def setUp(self):
        # 启动chrome浏览器
        self.driver = webdriver.Chrome()

    def testBaidu(self):
        self.driver.get("https://www.baidu.com")
        self.driver.find_element_by_id("kw").clear()
        self.driver.find_element_by_id("kw").send_keys(u"python")
        self.driver.find_element_by_id("su").click()
        time.sleep(5)
        assert u"python" in self.driver.page_source, "页面中不存在要搜索的关键字！"

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(SuiteTest1("testBaidu"))
#是为了设置生成的报表html文件地址。
    file_name = "D:\\test1.html" 
    # fp = file(file_name,'wb')
    fp = open(file_name, 'wb')
#此步是为了设置报表页面的title和报表总结描述内容。

    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Test_Report_Portal', description='Report_Description')    runner.run(suite)
    fp.close()
    print("测试完成！")
