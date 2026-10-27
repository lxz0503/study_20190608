import time,os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By


# 创建driver对象
driver = webdriver.Chrome()
# 浏览器窗口最大化
# driver.maximize_window()
# time.sleep(1)

url = os.getcwd() + '\\注册A.html'
# 打开指定的url
driver.get(url)
time.sleep(1)

# print("size: ", driver.find_element_by_id("AAA").size)
print("text: ", driver.find_element(by=By.ID,value="AAA").text)
print("属性值: ", driver.find_element(by=By.ID,value="AAA").get_property("href"))
# print("当前页面title: ", driver.title)
# print("当前页面url: ", driver.current_url)

print("span标签是否可见: ", driver.find_element(by=By.TAG_NAME, value="span").is_displayed())
print("标签是否可用: ", driver.find_element(by=By.ID, value="cancelA").is_enabled())


time.sleep(2)
driver.quit()
