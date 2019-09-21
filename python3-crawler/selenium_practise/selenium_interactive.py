# coding=utf-8
from selenium import webdriver
import time


browser = webdriver.Chrome()
browser.get('https://www.baidu.com/')
input_first = browser.find_element_by_id('kw')
input_first.send_keys('iphone')
button = browser.find_element_by_css_selector('input#su')    # 在页面上查找，能直接看到css路径,参考截图,
# 先将鼠标放在要点击的元素或者按钮，然后在右面查找对应的路径，此时页面上会显示css路径
# #表示根据id来查找
button.click()
time.sleep(3)
browser.quit()

#

# browser = webdriver.Chrome()
# browser.get('https://www.taobao.com')
# input_first = browser.find_element_by_id('q')
# input_first.send_keys('iphone')
# button = browser.find_element_by_css_selector('button.btn-search')    # 在页面上查找，能直接看到css路径,参考截图,
# # 先将鼠标放在要点击的元素或者按钮，然后在右面查找对应的路径，此时页面上会显示css路径
# # #表示根据id来查找
# button.click()
# time.sleep(3)
# browser.quit()


