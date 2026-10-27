# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://www.hao123.com/')
# 获取当前窗口句柄
current_handle = driver.current_window_handle
# 单击超链接
driver.find_element_by_link_text("hao123影视").click()
# 所有窗口句柄  列表类型
handles = driver.window_handles
print(handles)
# 切换到新窗口
driver.switch_to.window(handles[1])
driver.find_element_by_link_text("电影").click()
