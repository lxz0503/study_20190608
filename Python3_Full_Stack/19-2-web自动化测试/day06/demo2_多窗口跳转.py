import time,os
# 导入webdriver包
from selenium import webdriver
from selenium.webdriver.common.by import By

# 创建driver对象
driver = webdriver.Chrome()
# 最大化窗口
driver.maximize_window()
# 设置隐式等待时间
driver.implicitly_wait(30)
# 打开指定url
url = os.getcwd() + '\\注册A.html'
driver.get(url)
time.sleep(1)

# 获取当前窗口句柄
print("当前页:", driver.current_window_handle)
# 获取全部窗口句柄
print("所有:", driver.window_handles)

# xiaozhan 点击后出现新的页面
driver.find_element(by=By.ID,value="fwA").click()
print("关闭原页面前:", driver.window_handles)
time.sleep(1)

# 跳转到新的窗口
driver.switch_to.window(driver.window_handles[1])
print(driver.current_window_handle)
driver.find_element(by=By.ID,value="kw").send_keys("python")

driver.close()
# print("关闭原页面后:", driver.window_handles)

time.sleep(3)
driver.quit()
