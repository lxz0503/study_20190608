from selenium import webdriver
import unittest
import time
import HTMLTestRunner


class SogoWebTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.quit()

    def test_visitURL(self):
        url = "http://www.sogou.com"
        self.driver.get(url)
        title = self.driver.title
        print(title)
        assert self.driver.title.find(u"搜狗搜索") >= 0, "assert error"

    def test_visitRecentURL(self):
        first_url = "http://www.sogou.com"
        second_url = "https://www.baidu.com"   # this url should be https:// at office while http://at home
        self.driver.get(first_url)
        self.driver.get(second_url)
        self.driver.back()
        time.sleep(5)
        self.driver.forward()


if __name__ == '__main__':
    # unittest.main()                  # 必须注释掉这句话才能生成html报告,否则始终以unittest方式运行
    suite = unittest.TestSuite()
    # suite.addTest(WebTest('test_visitURL'))    # 运行单个case
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SogoWebTest))   # 运行整个测试套
    # file_name = "F:\\Pycharm\\Selenium_Xiaozhan\\report.html"
    file_name = "D:\\xiaozhan_git\\study_20190608\\API_Python\\web_api_selenium_unittest\\unit_test\\report.html"
    with open(file_name, 'wb+') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='report', description='web api test')
        runner.run(suite)