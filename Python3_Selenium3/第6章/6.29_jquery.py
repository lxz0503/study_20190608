# coding=utf-8
from selenium import webdriver

# jQuery 操作页面元素
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.baidu.com")
jq = "$('#kw').val('selenium')"
driver.execute_script(jq)
jq = "$('#su').click()"
driver.execute_script(jq)
import time
time.sleep(2)
driver.quit()
