# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://www.baidu.com')
driver.find_element_by_name('wd').send_keys('python')
