# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time

browser = webdriver.Chrome()
browser.get('https://www.taobao.com/')

try:
    wait = WebDriverWait(browser, 10, 0.2)
    # e = browser.find_element_by_css_selector('.mod-navbar div2')
    ele = wait.until(EC.presence_of_element_located((By.ID, 'q')))
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'btn-search')))
    print(ele)
    print(button)
except NoSuchElementException as e:
    print('no')
    print(e)
except TimeoutException as e:
    print('aaa')
    print(e.msg)
finally:
    browser.quit()
