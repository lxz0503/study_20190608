from datetime import datetime,date,timedelta
from selenium import webdriver

#以下为driver设置和打开携程火车票网站
driver =webdriver.Chrome()
'''
函数return_driver()是为了返回driver对象
'''
def return_driver():
    return driver
'''
函数open_base_site(url)是为了打开携程火车票首页面
'''
def open_base_site(url):
    #driver.get("https://trains.ctrip.com/TrainBooking/SearchTrain.aspx")
    driver.get(url)
'''
函数date_n(n) 为返回n天后的日期
'''
def date_n(n):
    return str((date.today() + timedelta(days = +int(n))).strftime("%Y-%m-%d"))
'''
函数id为返回按照id属性来定位元素的语句
'''
def id(element):
    return driver.find_element_by_id(element)

'''
函数css是返回按照css selector方式来定位元素的语句
'''
def css(element):
    return driver.find_element_by_css_selector(element)
'''
函数xpath是返回按照xpath方式来定位元素的语句
'''
def xpath(element):
    return driver.find_element_by_xpath(element)

'''
函数js为通过selenium来执行javascript语句
'''
def js(element):
    driver.execute_script("document.getElementById(" + "'" + element + "'" + ").removeAttribute('readonly')")
