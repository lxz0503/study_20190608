# coding=utf-8
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://www.baidu.com/')
# 获取文本值，即HTML标签<a></a>之间的文字内容
print(driver.find_element_by_link_text("新闻").text)
