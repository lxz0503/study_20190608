import time,os
# 导包
from selenium import webdriver
from selenium.webdriver.common.by import By


# 创建driver对象
driver = webdriver.Chrome()

url = os.getcwd() + '\\注册A.html'
print(url)
driver.get(url)

# input01 = driver.find_element_by_id("userA")
input01 = driver.find_element(by=By.ID, value="userA")
input01.send_keys("admin")
time.sleep(1)

# input02 = driver.find_element_by_name("passwordA")
input02 = driver.find_element(by=By.NAME, value="passwordA")
input02.send_keys("123456")
time.sleep(1)

# input03 = driver.find_element_by_class_name("telA")
input03 = driver.find_element(by=By.CLASS_NAME,value="telA")
input03.send_keys("18811110000")
time.sleep(1)

# xiaozhan  注意下面是find_elements  找到的是一串元input标签，取第三个
# driver.find_elements_by_tag_name("input")[3].send_keys("123@itcast.cn")
# driver.find_elements(by=By.TAG_NAME, value="input")[3].send_keys("123@itcast.cn")
input04 = driver.find_element(by=By.ID, value="emailA")
input04.send_keys("123@itcast.cn")

time.sleep(2)
driver.quit()
