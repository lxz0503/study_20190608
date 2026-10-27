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
# xiaozhan 下面是尝试抓取用pytest测试后的测试报告截图
driver.get('http://128.224.36.49:35359/index.html#graph')
time.sleep(1)

# driver.find_element(by=By.ID,value="userA").send_keys("admin")
# 给图片命名
img_name = time.strftime("%Y%m%d_%H%M%S")
# img_name = str(time.time()).replace(".", "_")
# 截图并生成图片
driver.get_screenshot_as_file("./images/%s.png" % img_name)

time.sleep(3)
driver.quit()

