#!/usr/bin/env python3
# encoding=utf-8
# @Time : 5/20/2021 5:32 PM
# @Author : xiaozhan Li
# @Email : lxz_20081025@163.com
# @File : 6.32.1_iframe.py
# coding=utf-8
from selenium import webdriver

# 一般登录用的用户名和密码都是嵌套在iframe里面
driver = webdriver.Chrome()
# 打开主页面QQ邮箱登录页面
driver.get('https://email.163.com/#from=ntes_product')
# 驱动切换到iframe，根据iframe的index切换
driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])
# 对用户名赋值
driver.find_element_by_name('email').send_keys('xiaozhan')
driver.find_element_by_css_selector("*[name='password']").send_keys('xiaozhan')
driver.find_element_by_css_selector("*[id='dologin']").click()
# 上面的代码已经切换到Frame内部，此时只能对Frame内部元素进行操作
# 如果要对Frame外部元素操作，需要退出，代码如下
driver.switch_to.default_content()
driver.find_element_by_link_text('企业邮箱').click()
# 退出浏览器操作
driver.quit()

