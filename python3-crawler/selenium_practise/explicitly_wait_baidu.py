#!/usr/bin/env python3
# encoding=utf-8
# @Time : 5/29/2021 11:25 AM
# @Author : xiaozhan Li
# @Email : lxz_20081025@163.com
# @File : explicitly_wait_baidu.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

driver = webdriver.Chrome()
driver.get("https://www.baidu.com/")
driver.find_element_by_id('kw').send_keys('柠檬班')
driver.find_element_by_id('su').click()
# wait until this element appears
ningmeng_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="3"]/h3/a')))

# operate this element
ningmeng_button.click()
time.sleep(1)
#
handles = driver.window_handles
print(handles)    # this is a list
# wait new window
# switch to new window or new frame to operate elements
print(driver.current_window_handle)   # current window handle
driver.switch_to.window(handles[-1])  # the newest one is the last
print(driver.title)
focus_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'j_head_focus_btn')))
focus_button.click()
time.sleep(3)
driver.quit()
# switch frame
# driver.switch_to.frame('frame_name')   # 自己去查找页面上的frame name是什么
# driver.switch_to.frame(1)
# driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])
# WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it('framename'))

# switch to alert
# WebDriverWait(driver, 10).until(EC.alert_is_present)  # wait this alert
# alert_ele = driver.switch_to.alert   # switch to this alert, return value is the alert
# print(alert_ele.text)
# alert_ele.accept()
# alert_ele.dismiss()
