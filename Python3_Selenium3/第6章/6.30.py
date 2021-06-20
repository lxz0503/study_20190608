#coding=utf-8
from selenium import webdriver
from selenium.webdriver import ActionChains

# 常用鼠标操作
driver = webdriver.Chrome()
driver.get('https://www.baidu.com')
driver.maximize_window()
element = driver.find_element_by_link_text(u"新闻")
#˫ 双击 ‘新闻’ 这个超链接
ActionChains(driver).double_click(element).perform()
import time
time.sleep(2)
driver.quit()
# 右键 单击 ‘新闻’
element = driver.find_element_by_link_text('地图')
ActionChains(driver).context_click(element).perform()
time.sleep(2)
# driver.quit()
