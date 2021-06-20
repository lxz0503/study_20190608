# coding=utf-8
from selenium import webdriver

# 利用JavaScript 操作页面元素
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.baidu.com")
print(f'current url is {driver.current_url}')
print(f'window handle is {driver.current_window_handle}')
js = "document.getElementById('kw').value = 'selenium'"    # 可以在console里面执行这条命令
driver.execute_script(js)
import time
time.sleep(2)
driver.quit()
