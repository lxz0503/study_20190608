# coding=utf-8
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('https://www.baidu.com/')
print(driver.title)
