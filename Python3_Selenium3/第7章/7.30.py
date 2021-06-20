from selenium import webdriver
from PIL import Image
driver = webdriver.Chrome()
driver.get("https://pan.baidu.com/")
cookies=driver.get_cookies()
print(cookies)
