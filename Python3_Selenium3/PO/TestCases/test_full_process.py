import HTMLTestRunner
import unittest

from selenium import webdriver

from Common.excelData import read_excel
from Common.function import configUrl
from Common.function import projectPath
from PageObject.book_page import BookPage
from PageObject.order_page import OrderPage
from PageObject.search_page import SearchPage


class BookTicketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_excel(projectPath() + "Data/testdata.xlsx", 0)
        cls.driver = webdriver.Chrome()      # 真正测试的时候采取初始化self.driver
        cls.driver.get(configUrl())
        cls.driver.maximize_window()

    # 下面直接明文定位了元素，这种可以用ddt，把数据放在字典组成的列表
    def test_02(self):
        # self.driver.get("http://trains.ctrip.com/TrainBooking/SearchTrain.aspx###")
        search = SearchPage(self.driver)
        res = search.search_train(self.data.get(1)[0], self.data.get(1)[1], self.data.get(1)[2])
        # 本例断言是根据当前页面的url去判断的
        # self.assertIn('TrainBooking', res)
        self.assertTrue(search.is_exist_ele('your element like //a[@name="xiaozhan"]'))

    def test_03(self):
        book = BookPage(self.driver)
        res = book.book_btn()
        self.assertIn("InputPassengers", res)

    def test_04(self):
        order = OrderPage(self.driver)
        order.user_info("小王")

    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    suiteTest = unittest.TestSuite()
    suiteTest.addTest(BookTicketTest("test_02"))
    suiteTest.addTest(BookTicketTest("test_03"))
    suiteTest.addTest(BookTicketTest("test_04"))
    filepath = "re.html"
    with open(filepath, 'wb') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='自动化测试报告', description="测试报告")
        runner.run(suiteTest)
