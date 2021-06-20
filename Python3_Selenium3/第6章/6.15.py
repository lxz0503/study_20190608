# coding=utf-8
from selenium import webdriver


driver = webdriver.Chrome()
driver.get('https://www.baidu.com/')
driver.find_element_by_id('kw').send_keys('Selenium')
driver.find_element_by_id('kw').clear()
