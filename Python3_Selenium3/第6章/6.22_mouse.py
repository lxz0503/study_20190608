# coding=utf-8
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains

# 特殊元素定位，鼠标悬停操作
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.baidu.com")
bg_config = driver.find_element_by_id('s-usersetting-top')   # page 83，修改为find by id
# move_to_element方法可以模拟将鼠标停在 链接 设置 处
ActionChains(driver).move_to_element(bg_config).perform()
# 鼠标悬停时，定位元素， 超链接  搜索设置   然后  单击操作
driver.find_element_by_link_text('搜索设置').click()
time.sleep(3)
# 修改书上page 84代码如下
# driver.find_element_by_xpath("//*[@for='nr_2']").click()
driver.find_element_by_css_selector("*[for='nr_2']").click()
#
import time
time.sleep(2)
# 判断选择框 是否勾选
print(driver.find_element_by_css_selector("*[id='nr_2']").is_selected())
# print(driver.find_element_by_xpath("//*[@id='nr_2']").is_selected())

# driver.quit()
