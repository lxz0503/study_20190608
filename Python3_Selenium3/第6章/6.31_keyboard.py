# coding=utf-8
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


driver = webdriver.Chrome()
driver.get('https://www.baidu.com')
driver.implicitly_wait(10)
driver.maximize_window()
driver.find_element_by_id("kw").send_keys("SeleniumTest")
driver.find_element_by_id("kw").send_keys(Keys.BACK_SPACE)   # 删除键
# 也可以合并最后两行
# driver.find_element_by_id("kw").send_keys("SeleniumTest" + Keys.BACK_SPACE)
driver.find_element_by_id('kw').send_keys("SeleniumTest" + Keys.ENTER)
# ctrl+A   ctrl +x, ctrl+v
driver.find_element_by_id('kw').send_keys(Keys.CONTROL, 'a')
time.sleep(2)
driver.find_element_by_id('kw').send_keys(Keys.CONTROL, 'x')
time.sleep(2)
driver.find_element_by_id('kw').send_keys(Keys.CONTROL, 'v')

# 常用的键盘事件如下
# Keys.BACK_SPACE
# Keys.SPACE
# Keys.TAB
# Keys.CONTROL, 'a'
# Keys.CONTROL, 'x'
# Keys.CONTROL, 'v'
# Keys.CONTROL, 'c'
# Keys.F1



