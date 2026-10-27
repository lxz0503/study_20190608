import time,os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


# 创建driver对象
driver = webdriver.Chrome()
action = ActionChains(driver)

# 浏览器窗口最大化
# driver.maximize_window()
# time.sleep(1)

url = os.getcwd() + '\\注册A.html'
# 打开指定的url
driver.get(url)
time.sleep(1)

userA = driver.find_element(by=By.ID,value="userA")
userA.send_keys("admin")
# 右击
action.context_click(userA).perform()
# 双击  xiaozhan 这个没啥意义,看不出效果
time.sleep(2)
action.double_click(userA).perform()

time.sleep(2)
driver.quit()