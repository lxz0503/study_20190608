#!usr/bin/env python
# coding=UTF-8
from selenium.webdriver.support.expected_conditions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver


class WebDriver(object):
    def __init__(self, driver):
        self.driver = driver

    def findElement(self, *loc):
        '''find one element'''
        try:
            # return self.driver.find_element(*loc)
            return WebDriverWait(self.driver, 20).until(lambda x: x.find_element(*loc))
        except NoSuchElementException as e:
            print('Error details are {0}'.format(e.args[0]))

    def findElements(self, *loc):
        '''find more elements'''
        try:
            # return self.driver.find_elements(*loc)
            return WebDriverWait(self.driver, 20).until(lambda x: x.find_elements(*loc))
        except NoSuchElementException as e:
            print('Error details are {0}'.format(e.args[0]))

# test code for above class
if __name__ == '__main__':
    driver = webdriver.Firefox()
    driver.get('http://www.baidu.com')
    t = WebDriver(driver)
    search_box = t.findElement('id', 'kw')
    print(search_box.tag_name)
    driver.quit()

