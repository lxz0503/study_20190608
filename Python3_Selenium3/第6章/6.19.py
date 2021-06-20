# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('http://www.baidu.com')
# 浏览器向后
driver.back()
# 浏览器向前
driver.forward()
