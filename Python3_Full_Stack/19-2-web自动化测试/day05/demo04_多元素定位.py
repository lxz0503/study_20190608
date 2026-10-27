import time,os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By


# 创建driver对象
driver = webdriver.Chrome()


url = os.getcwd() + '\\注册A.html'

# 打开指定的url
driver.get(url)

# input04 = driver.find_elements_by_tag_name("input")  # selenium 老版本的语法
input04 = driver.find_elements(by=By.TAG_NAME, value="input")   # selenium4.4版本的语法
# print(type(input04))
# print(len(input04))
print(input04)

input04[3].send_keys("123@itcast.cn")

time.sleep(3)
# 关闭浏览器
driver.quit()

