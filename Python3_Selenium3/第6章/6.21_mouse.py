# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# 特殊元素定位，鼠标悬停操作
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.baidu.com")
# 找到元素
bg_config = driver.find_element_by_id('s-usersetting-top')   # page 83，修改为find by id
# move_to_element方法可以模拟将鼠标停在 链接 设置 处,
ActionChains(driver).move_to_element(bg_config).perform()
# 鼠标悬停时，定位元素， 超链接  搜索设置   然后  单击操作
driver.find_element_by_link_text('搜索设置').click()

