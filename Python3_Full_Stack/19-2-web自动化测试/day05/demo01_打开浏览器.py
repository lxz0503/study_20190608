import time, os
# 导包
from selenium import webdriver

# 创建driver对象
driver = webdriver.Chrome()

# url = "https://www.baidu.com"
print(os.getcwd() + '\\注册A.html')
url = os.getcwd() + '\\注册A.html'
# url = r"C:\Users\DOU\Desktop\day05-web自动化测试\02-资料\素材\注册A.html"
# url = "C:\\Users\\DOU\\Desktop\\day05-web自动化测试\\02-资料\\素材\\注册A.html"
# url = "C:/Users/DOU/Desktop/day05-web自动化测试/02-资料/素材/注册A.html"
# 打开指定的url
driver.get(url)

time.sleep(3)

# 关闭浏览器
driver.quit()
