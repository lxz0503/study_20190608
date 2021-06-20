#!/usr/bin/env python3
# encoding=utf-8
# @Time : 6/19/2021 1:38 PM
# @Author : xiaozhan Li
# @Email : lxz_20081025@163.com
# @File : test_search.py.py
import HTMLTestRunner
import unittest
import time
from ddt import ddt,data,unpack

from selenium import webdriver

from Common.excelData import pd_read_excel
from Common.function import configUrl
from Common.function import projectPath
from PageObject.search_page import SearchPage

from selenium.webdriver.common.by import By
import os

# filename = os.path.split(os.path.realpath(__file__))[0].split('C')[0] + "Data\\testdata.xlsx"
filename = os.path.split(os.path.realpath(__file__))[0].split('T')[0] + "Data\\testdata.xlsx"

sheet_name = 'xiaozhan'
test_data = pd_read_excel(filename, sheet_name)

@ddt
class SearchTicketTest(unittest.TestCase):
    leave = '北京'
    arrive = '上海'
    train = (By.XPATH, "//*[@trainname='D709']")   # until you find this information which means search is successful

    @classmethod
    def setUpClass(cls):
        # cls.data = read_excel(projectPath() + "Data/testdata.xlsx", 0)
        cls.driver = webdriver.Chrome()      # 真正测试的时候采取初始化self.driver
        cls.driver.get(configUrl())
        cls.driver.maximize_window()
        cls.ses = SearchPage(cls.driver)  # must have self.driver

    # 下面直接明文定位了元素，这种可以用ddt，把数据放在字典组成的列表
    def test_search(self):
        self.ses.search_leave().send_keys(self.leave)
        time.sleep(2)
        self.ses.search_arrive().send_keys(self.arrive)
        time.sleep(2)
        self.ses.remove_readonly()
        self.ses.search_date()
        time.sleep(5)
        # 点击搜索按钮
        self.ses.search_btn()
        # 判断是否执行成功，判断是否出现相应的元素
        self.assertTrue(self.ses.is_exist_ele(self.train))

    @data(*test_data)
    @unpack
    def test_ddt(self, leave, arrive, riqi, checi, mingzi, id):
        # print(a,b,c,d,e,f)
        self.ses.search_leave().send_keys(leave)
        time.sleep(2)
        self.ses.search_arrive().send_keys(arrive)
        time.sleep(2)
        self.ses.remove_readonly()
        self.ses.search_date(riqi)
        time.sleep(5)
        # 点击搜索按钮
        self.ses.search_btn()
        # 判断是否执行成功，判断是否出现相应的元素
        self.assertTrue(self.ses.is_exist_ele(checi))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    suiteTest = unittest.TestSuite()
    suiteTest.addTest(SearchTicketTest("test_ddt"))
    # suiteTest.addTest(SearchTicketTest("test_03"))
    # suiteTest.addTest(SearchTicketTest("test_04"))
    filepath = "re.html"
    with open(filepath, 'wb') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='自动化测试报告', description="测试报告")
        runner.run(suiteTest)

