from datetime import datetime,date,timedelta
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
#以下为定义函数部分，其目的是为了返回今天后的第n天的日期，格式为“2019-04-06”
def date_n(n):
    return str((date.today() + timedelta(days = +int(n))).strftime("%Y-%m-%d"))
#以下变量为定义搜索火车票的出发站和到达站。
from_station = "上海"
to_station = "杭州"
#以下为tomorrow变量
tomorrow = date_n(1)
driver = webdriver.Chrome()
driver.get("https://trains.ctrip.com/TrainBooking/SearchTrain.aspx")
#以下为定位出发城市和到达城市的页面元素，并且设置其值为以上定义值。
driver.find_element_by_id("notice01").send_keys(from_station)
driver.find_element_by_id("notice08").send_keys(to_station)
#以下代码为移除出发时间的'readonly'属性。
driver.execute_script("document.getElementById('dateObj').removeAttribute('readonly')")
time.sleep(2)
#清除出发时间的默认内容。
driver.find_element_by_id("dateObj").clear()
time.sleep(2)
#以下为定义搜索车次日期。
driver.find_element_by_id("dateObj").send_keys(tomorrow)
#以下步骤是为了解决日期控件弹出窗在输入日期后无法消失的问题，从而影响测试的进行。
#原理是为了让鼠标左键点击页面空白处。
ActionChains(driver).move_by_offset(0,0).click().perform()
#以下为点击车次搜索按钮
driver.find_element_by_id("searchbtn").click()
#在页面跳转时最好是加一些时间等待的步骤，免得有一些元素定位的异常出现。
time.sleep(2)
#在车次K1805车次的硬座区域点击预定按钮，来预定车票
driver.find_element_by_css_selector("#tbody-01-K18050 > div.railway_list > div.w6 > div:nth-child(1) > a").click()
#如下步骤是为了实现不用登录到携程系统而实现订票的目的。
driver.find_element_by_id("btn_nologin").click()
