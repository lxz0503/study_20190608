import time, os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By

# 创建driver对象
driver = webdriver.Chrome()

url = os.getcwd() + '\\注册A.html'

# 打开指定的url
driver.get(url)

# link1 = driver.find_element_by_link_text("AA 百度 网站")
# link1 = driver.find_element_by_partial_link_text("AA")   # 适用于老的selenium版本
link1 = driver.find_element(by=By.PARTIAL_LINK_TEXT, value="AA")  # selenium 4.4版本语法
link1.click()

time.sleep(3)
# 关闭浏览器
driver.quit()
