# coding=utf-8
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time


browser = webdriver.Chrome()
url = 'https://www.baidu.com'
browser.get(url)
button = browser.find_element_by_css_selector('input#su')
# print(button.get_attribute('class'))
print(button.size)
print(button.tag_name)
print(button.id)
print(button.location)
time.sleep(2)
browser.quit()
#

browser = webdriver.Chrome()
url = 'https://www.baidu.com'
browser.get(url)
try:
    button = browser.find_element_by_css_selector('input#su>link')
# print(button.get_attribute('class'))
except NoSuchElementException:
    print('no such button')
finally:
    time.sleep(2)
    browser.quit()

