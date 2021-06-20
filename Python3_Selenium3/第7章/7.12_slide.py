# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
driver = webdriver.Chrome()
driver.get("https://passport.ctrip.com/user/reg/home")
driver.find_element_by_xpath('//*[@class="reg_btn reg_agree"]').click()   # by xpath
# driver.find_element_by_css_selector('*[class="reg_btn reg_agree"]').click()   # by selector
time.sleep(3)
# 以下是为了获取滑块元素
sour = driver.find_element_by_css_selector("*[class='cpt-drop-btn']")
print(sour.size['width'])     # 40
print(sour.size["height"])    # 40
# 以下是为了获取滑块区域元素
ele = driver.find_element_by_css_selector("*[class='cpt-bg-bar']")
print(ele.size['width'])      # 268
print(ele.size["height"])     # 40
# 拖动滑块,注意理解滑块的位置，宽度和高度, 尤其那个负号
ActionChains(driver).drag_and_drop_by_offset(sour, ele.size['width'], -sour.size["height"]).perform()
