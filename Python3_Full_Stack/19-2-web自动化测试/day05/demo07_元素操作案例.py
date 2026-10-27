import time,os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By


# 创建driver对象
driver = webdriver.Chrome()
url = os.getcwd() + '\\注册A.html'
# 打开指定的url
driver.get(url)
# 设置要输入内容的列表
text_list = ['admin', '123456', '18611111111', '123@qq.com']
# 获取前四个input标签
# inputs = driver.find_elements_by_css_selector("p>input")   # selenium 3的语法
inputs = driver.find_elements(by=By.CSS_SELECTOR, value="p>input")   # selenium 4.4的语法
# print(inputs)
for i in range(4):
    inputs[i].send_keys(text_list[i])
    time.sleep(1)

inputs[3].clear()

# 获取id为AAA的标签   #表示获取元素id
a = driver.find_element(by=By.CSS_SELECTOR, value="#AAA")
# 点击
a.click()

time.sleep(3)
# 关闭浏览器
driver.quit()
