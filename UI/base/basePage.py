#!usr/bin/env python
# coding=UTF-8

from selenium import webdriver
from selenium.webdriver.support.expected_conditions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time


class WebDriver(object):
    def __init__(self, driver):
        self.driver = driver

    def findElement(self, *loc):
        '''find one element'''
        try:
            # return self.driver.find_element(*loc)
            return WebDriverWait(self.driver, 20).until(lambda x:x.find_element(*loc))
        except NoSuchElementException as e:
            print('Error details are {0}'.format(e.args[0]))

    def findElements(self, *loc):
        '''find more elements'''
        try:
            # return self.driver.find_elements(*loc)
            return WebDriverWait(self.driver, 20).until(lambda x: x.find_elements(*loc))
        except NoSuchElementException as e:
            print('Error details are {0}'.format(e.args[0]))
