#encoding = utf-8
import unittest
from selenium import webdriver
import time
#driver = webdriver.chrome()
class add(unittest.TestCase): #声明一个测试类
    def setUp(self):
        #启动chrome浏览器
        self.driver = webdriver.Chrome()

    def testBaidu(self):
        self.driver.get("https://www.baidu.com")
        self.driver.find_element_by_id("kw").clear()
        self.driver.find_element_by_id("kw").send_keys(u"python")
        self.driver.find_element_by_id("su").click()
        time.sleep(5)
        assert u"python" in self.driver.page_source,"页面中不存在要搜索的关键字！"

    def tearDown(self):
        self.driver.quit()

if __name__ == '__main__':
    unittest.main()
