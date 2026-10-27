import time,os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By

# 创建driver对象
driver = webdriver.Chrome()


url = os.getcwd() + '\\注册A.html'

# 打开指定的url
driver.get(url)

# input01 = driver.find_element_by_xpath("//input[@id='userA']")
# selenium4.4的语法 如下
input01 = driver.find_element(by=By.XPATH, value="//input[@id='userA']")

time.sleep(3)
# 关闭浏览器
driver.quit()
