# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://www.baidu.com/')
print(driver.find_element_by_tag_name('form').get_attribute('name'))
