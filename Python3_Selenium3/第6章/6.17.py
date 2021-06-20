# coding=utf-8
from selenium import webdriver

# page 79,补充一些操作
driver = webdriver.Chrome()
driver.get('https://www.baidu.com/')
print(driver.current_url)    # 打印当前网页地址
print(driver.find_element_by_id('kw').is_enabled())  # 判断页面元素是否可用,返回True 或者False
print(driver.find_element_by_id('kw').is_displayed())  # 判断页面元素是否显示,返回True 或者False
#
from selenium import webdriver
import time

driver.find_element_by_id("s-usersetting-top").click()
time.sleep(3)
# print(driver.find_element_by_xpath("//input[@id='nr_1']").is_selected())
# driver.quit()

