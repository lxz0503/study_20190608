import time
# 导入webdriver包
from selenium import webdriver

# 创建driver对象
driver = webdriver.Chrome()
# 最大化窗口
driver.maximize_window()
# 设置隐式等待时间
driver.implicitly_wait(30)
# 打开指定url
driver.get("https://www.baidu.com")
time.sleep(1)

# driver.find_element_by_id("userA").send_keys("admin")
# print(driver.get_cookies())
# print(driver.get_cookies())

driver.add_cookie({"name": "BDUSS", "value": "DNvQlFzZUxsZ1VzRUd5T2dwTnE3elZySTM5T1FkT05MejFZeVFmdkVCYUFiUVJkSVFBQUFBJCQAAAAAAAAAAAEAAADQPwENxvy-ocfgy78AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIDg3FyA4NxcR"})
time.sleep(1)
driver.refresh()
print(driver.get_cookies())

time.sleep(2)
driver.quit()

