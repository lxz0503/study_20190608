#!/usr/bin/env python3
# encoding=utf-8
# @Time : 4/26/2021 9:29 PM
# @Author : xiaozhan Li
# @Email : lxz_20081025@163.com
# @File : base_unit.py
import unittest
from Common.function import configUrl
from selenium import webdriver


class UnitBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.driver = webdriver.Chrome()
        cls.driver.get(configUrl())
        cls.driver.maximize_window()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
