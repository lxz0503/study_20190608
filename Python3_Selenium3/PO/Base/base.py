#!/usr/bin/env python3
# coding=utf-8
from Common.log_size_rotate import FrameLog   # 这里导入后，其他地方就没必要再次导入了，会报错
from datetime import date, timedelta

# 对base代码进行优化、增加
class Base(object):
    def __init__(self, driver):
        self.driver = driver
        self.log = FrameLog().log()

    # 元组的方式来定位，定位方法和元素组成一个元组, element is a tuple
    def find_ele(self, element):
        return self.driver.find_element(element)

    # id
    def by_id(self, element):
        return self.driver.find_element_by_id(element)

    # name
    def by_name(self, element):
        return self.driver.find_element_by_name(element)

    # class name
    def by_class_name(self, element):
        return self.driver.find_element_by_class_name(element)

    # xpath
    def by_xpath(self, element):
        return self.driver.find_element_by_xpath(element)

    # css
    def by_css(self, element):
        return self.driver.find_element_by_css_selector(element)

    # check date
    def date_n(self, n):
        return str((date.today() + timedelta(days=+int(n))).strftime("%Y-%m-%d"))

    # run js
    def js(self, element):
        self.driver.execute_script(element)

    # url
    def dr_url(self):
        return self.driver.current_url

    # 前进
    def forward(self):
        self.driver.forward()

    # 后退
    def back(self):
        self.driver.back()

    # 退出
    def quit(self):
        self.driver.quit()

