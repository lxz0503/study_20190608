# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://www.baidu.com/')
#执行后，输入框输入字符“Selenium”
driver.find_element_by_id('kw').send_keys("Selenium")

