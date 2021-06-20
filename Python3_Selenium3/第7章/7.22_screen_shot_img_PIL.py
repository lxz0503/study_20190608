# coding=utf-8
from selenium import webdriver
import time
from PIL import Image
driver = webdriver.Chrome()
driver.get("https://user.qunar.com/passport/login.jsp?")
driver.maximize_window()
time.sleep(3)
# 整个屏幕截图
driver.save_screenshot("qu.png")
# 找到验证码截图所在位置
imgcode = driver.find_element_by_css_selector("div[class='qr-show']")
left = imgcode.location['x']
top = imgcode.location['y']
right = left+imgcode.size['width']
bottom = top+imgcode.size['height']
# 单独生成 验证码图片
im = Image.open("qu.png")
im = im.crop((left, top, right, bottom))
im.save('t.png')
