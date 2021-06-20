#!/usr/bin/env python3
# encoding=utf-8
# @Time : 5/20/2021 2:45 PM
# @Author : xiaozhan Li
# @Email : lxz_20081025@163.com
# @File : 6.30.1.py
#coding=utf-8
from selenium import webdriver
from selenium.webdriver import ActionChains
import time

# 常用鼠标操作
driver = webdriver.Chrome()
driver.get('https://www.baidu.com')
driver.maximize_window()
element = driver.find_element_by_link_text('地图')
# 右键 单击 ‘地图’
ActionChains(driver).context_click(element).perform()
time.sleep(2)
driver.quit()