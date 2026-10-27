# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://www.baidu.com')
# ִ获取 百度一下 这个提交按钮的value属性值, 会输出  百度一下
print(driver.find_element_by_id('su').get_attribute('value'))   # 百度一下
print(driver.find_element_by_id('su').get_attribute('type'))    # submit
