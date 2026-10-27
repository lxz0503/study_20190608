
import time,os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By


from selenium.webdriver.support.select import Select
# 创建driver对象
driver = webdriver.Chrome()

url = os.getcwd() + '\\注册A.html'
# 打开指定的url
driver.get(url)
time.sleep(1)

# 常见select对象
select = Select(driver.find_element(by=By.ID, value="selectA"))

# # 通过索引选择 索引从0开始
# select.select_by_index(1)
# time.sleep(2)
#
# # 通过属性value的值选择
# select.select_by_value("gz")
# time.sleep(2)
#
# # 通过html显示内容选择
# select.select_by_visible_text("A重庆")

# print(select.options)
# print(len(select.options))

# 所有option标签对象都存在select.options里, 是个列表
for option in select.options:
    option.click()
    time.sleep(2)

time.sleep(2)
driver.quit()
