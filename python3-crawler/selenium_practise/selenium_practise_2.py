# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Chrome()
browser.get('http://news.baidu.com/')
# 有空格，表示先搜索class名字为mod-navbar,然后再查找下面的tag为div
lis = browser.find_elements_by_css_selector('.mod-navbar div')
# lis = browser.find_elements(By.CSS_SELECTOR, '.mod-navbar div')
print(lis)
browser.close()