###
###配套视频已出版，学习有疑问联系作者qq:2574674466###
###
# _*_coding:utf-8_*_
import os, sys

sys.path.append(os.path.split(os.getcwd())[0])
import time, unittest, HTMLTestRunner
from PageObject.bookPage import bookPage
from PageObject.orderPage import orderPage
from PageObject.searchPage import searchPage
from PageObject.login_page import LoginPage
from Common.excelData import read_excel
from Common.function import configUrl
from selenium import webdriver
from Common.function import projectPath



class logingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('tt')
        cls.data = read_excel(projectPath() + "Data/testdata.xlsx", 0)
        print(cls.data.get(1)[0])
        # 这个path过书中出现比较多，可以放环境变量中，书里这一步省略
        path = 'D:/soft/webdriver/chromedriver.exe'
        cls.driver = webdriver.Chrome(path)
        cls.driver.get(configUrl())
        cls.driver.maximize_window()

    def test_02(self):
        self.driver.get("http://trains.ctrip.com/TrainBooking/SearchTrain.aspx###")
        search = searchPage(self.driver)
        res = search.searchTrain(self.data.get(1)[0], self.data.get(1)[1], self.data.get(1)[2])
        # 本例断言是根据当前页面的url去判断的
        self.assertIn('TrainBooking', res)

    def test_03(self):
        book = bookPage(self.driver)
        res = book.bookBtn()
        self.assertIn("InputPassengers", res)

    def test_04(self):
        order = orderPage(self.driver)
        order.userInfo("小王")

    # 登录的时候一般会判断是否进入登录页面，通过是否出现某个元素来判断
    def test_05(self):
        lg = LoginPage(self.driver)
        lg.login()
        self.assertTrue(lg.is_exist_ele())

    # 如果登录错误，会有各种提示
    def test06(self):
        lg = LoginPage(self.driver)
        lg.login()
        self.assertEqual(lg.get_error_info(), '请输入正确的手机号')

    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    suiteTest = unittest.TestSuite()
    suiteTest.addTest(logingTest("test_02"))
    suiteTest.addTest(logingTest("test_03"))
    suiteTest.addTest(logingTest("test_04"))
    filepath = "C:\\re.html"
    fp = open(filepath, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='自动化测试报告', description="测试报告")
    runner.run(suiteTest)
    fp.close()
