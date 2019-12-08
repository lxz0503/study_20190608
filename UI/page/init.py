#!/usr/bin/env python
# encoding=UTF-8

import unittest
from selenium import webdriver
from utils.operationXml import *


class Init(unittest.TestCase, OperationXml):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.driver.get(self.getXmlData('url'))

    def tearDown(self):
        self.driver.quit()