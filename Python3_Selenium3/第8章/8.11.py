from selenium import webdriver
import time
driver = webdriver.Chrome()
driver.get("https://trains.ctrip.com/TrainBooking/SearchTrain.aspx")
#以下变量为定义搜索火车票的出发站和到达站。
from_station = "上海"
to_station = "杭州"
#以下为定位出发城市和到达城市的页面元素，并且设置其值为以上定义值。
driver.find_element_by_id("notice01").send_keys(from_station)
driver.find_element_by_id("notice08").send_keys(to_station)
#以下代码为移除出发时间的'readonly'属性。
driver.execute_script("document.getElementById('dateObj').removeAttribute('readonly')")
#以下为定义搜索车次日期。
driver.find_element_by_id("dateObj").send_keys("2019-04-12")
#以下为定位车次搜索按钮
driver.find_element_by_id("searchbtn").click()
