# !/usr/bin/ env python
# encoding=utf-8
from lettuce import *
from selenium import webdriver
import time


@step('I have the english name "(.*)"')
def have_the_search_word(step, search_word):
    world.search_word = str(search_word)
    print(world.search_word)


@step('I search it in sogou website')
def search_in_sogou_website(step):
    world.driver = webdriver.Firefox()
    world.driver.get('http://www.sogou.com')
    world.driver.find_element_by_id('query').send_keys(world.search_word)
    world.driver.find_element_by_id('stb').click()
    time.sleep(5)


@step('I see the entire name "(.*)"')
def check_result_in_sogou(step, search_result):
    assert search_result in world.driver.page_source, "got word %s" % search_result
    world.driver.quit()


