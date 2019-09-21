# coding=utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time

browser = webdriver.Chrome()
browser.get('http://news.baidu.com/')
browser.implicitly_wait(10)
try:
    # ele = browser.find_element_by_css_selector('.mod-navbar div')
    ele = browser.find_element_by_css_selector('.mod-navbar div2')
except NoSuchElementException as e:
    print(e)
except TimeoutException as e:
    print(e)
finally:
    time.sleep(3)
    browser.quit()

