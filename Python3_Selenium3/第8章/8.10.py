
###
###配套视频已出版，学习有疑问联系作者qq:2574674466###
###
#coding=utf-8
'''
实现火车票查询的页面元素的功能。
'''
from selenium import webdriver
import time
driver = webdriver.Chrome()
driver.get("https://trains.ctrip.com/TrainBooking/SearchTrain.aspx")
#以下变量为定义搜索火车票的出发站和到达站。
from_station = "上海"
to_station = "杭州"
#以下为定位出发城市和到达城市的页面元素
driver.find_element_by_id("notice01").send_keys(from_station)
driver.find_element_by_id("notice08").send_keys(to_station)
driver.find_element_by_id("dateObj").send_keys("2019-04-12")
#以下为定位车次搜索按钮
driver.find_element_by_id("searchbtn").click()
