
import time,os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


# 创建driver对象
driver = webdriver.Chrome()
# 创建action对象
action = ActionChains(driver)

# 浏览器窗口最大化
# driver.maximize_window()
# time.sleep(1)

url = os.getcwd() + '\\drag.html'
# 打开指定的url
driver.get(url)
time.sleep(1)

source = driver.find_element(by=By.ID, value="div1")
target = driver.find_element(by=By.ID, value="div2")
time.sleep(1)
action.drag_and_drop(source, target).perform()


time.sleep(2)
driver.quit()