# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://www.baidu.com")
# 选择class=s_ipt的元素，也就是页面上的输入框
driver.find_element_by_css_selector('.s_ipt').send_keys('python')
# 选择id=kw的元素，也就是页面上的输入框
driver.find_element_by_css_selector('#kw').send_keys('xiaozhan')
# 根据输入框标签input内部设置的属性值name='wd'来定位输入框,相对路径
driver.find_element_by_css_selector("input[name='wd']").send_keys('python')
# 根据输入框标签input内部设置的属性值name='wd'来定位输入框,相对路径
driver.find_element_by_css_selector("*[name='wd']").send_keys('name')
import time
time.sleep(1)
# driver.find_element_by_css_selector("input[name='wd']").clear()
