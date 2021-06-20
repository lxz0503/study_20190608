from datetime import datetime,date,timedelta
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
#以下为定义函数部分，其目的是为了返回今天后的第n天的日期，格式为“2019-04-06”
def date_n(n):
    return str((date.today() + timedelta(days = +int(n))).strftime("%Y-%m-%d"))

def id(element):
    return driver.find_element_by_id(element)

def css(element):
    return driver.find_element_by_css_selector(element)
def js(element):
    driver.execute_script("document.getElementById(" + "'" + element + "'" + ").removeAttribute('readonly')")
def xpath(element):
    return driver.find_element_by_xpath(element)

#以下变量为定义搜索火车票的出发站和到达站。
from_station = "上海"
to_station = "杭州"

#以下为tomorrow变量
tomorrow = date_n(1)
#以下为driver设置
driver = webdriver.Chrome()
driver.get("https://trains.ctrip.com/TrainBooking/SearchTrain.aspx")

#以下为定位出发城市和到达城市的页面元素，并且设置其值为以上定义值。
id("notice01").send_keys(from_station)
id("notice08").send_keys(to_station)

#以下代码为移除出发时间的'readonly'属性。
js("dateObj")

time.sleep(2)
#清除出发时间的默认内容。
id("dateObj").clear()
time.sleep(2)
#以下为定义搜索车次日期。
id("dateObj").send_keys(tomorrow)

#以下步骤是为了解决日期控件弹出窗在输入日期后无法消失的问题，从而影响测试的进行。
#原理是为了让鼠标左键点击页面空白处。
ActionChains(driver).move_by_offset(0,0).click().perform()

#以下为点击车次搜索按钮
id("searchbtn").click()

#在页面跳转时最好是加一些时间等待的步骤，免得有一些元素定位的异常出现。
time.sleep(2)

#在车次K1805车次的硬座区域点击预定按钮，来预定车票
xpath("//div[starts-with(@id,'tbody-01-K1805')]/div[1]/div[6]/div[1]/a").click()
time.sleep(5)
#浏览器窗口最大化
driver.maximize_window()
id("btn_nologin").click()
time.sleep(3)
#订单信息页面输入乘客姓名信息
css("#pasglistdiv > div > ul > li:nth-child(2) > input").send_keys("小刘")
