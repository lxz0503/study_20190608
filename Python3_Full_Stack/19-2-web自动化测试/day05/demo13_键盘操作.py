import time, os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 创建driver对象
driver = webdriver.Chrome()

url = os.getcwd() + '\\注册A.html'
# 打开指定的url
driver.get(url)
time.sleep(1)

# 获取两个元素
userA = driver.find_element(by=By.ID, value="userA")
emailA = driver.find_element(by=By.ID, value="emailA")

userA.send_keys('admin123')
time.sleep(1)
# 删除
userA.send_keys(Keys.BACK_SPACE)
time.sleep(1)
# 从第一个元素里全选 复制 ctrl+a ctrl+c 两个选一个就行
# userA.send_keys(Keys.CONTROL, "a")  # 或者用下面的ctrl + c
userA.send_keys(Keys.CONTROL, "c")
# 在第二个元素里粘贴 ctrl+v
emailA.send_keys(Keys.CONTROL, "v")


time.sleep(2)
driver.quit()