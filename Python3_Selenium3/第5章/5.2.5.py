# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://www.baidu.com')
# 打开新闻
driver.find_element_by_partial_link_text('新').click()
