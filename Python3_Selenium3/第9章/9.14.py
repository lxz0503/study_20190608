'''
此页面是为了测试火车票查询的页面元素的功能。
'''
from selenium.webdriver.common.action_chains import ActionChains
from functions import date_n,id,css,xpath,js,return_driver,open_base_site
#from selenium import webdriver
import time

#以下变量为定义搜索火车票的出发站和到达站。
driver =return_driver()
open_base_site("https://trains.ctrip.com/TrainBooking/SearchTrain.aspx")
from_station = "上海"
to_station = "杭州"

#以下为tomorrow变量
tomorrow = date_n(1)

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

#在车次K1805车次的硬座区域点击预定按钮，来预定车票,
#此处为了代码的健壮，需要用到xpath＋模拟查询来增强测试代码
xpath("//div[starts-with(@id,'tbody-01-K1805')]/div[1]/div[6]/div[1]/a").click()

#如下步骤是为了实现不用登录到携程系统而实现订票的目的。
time.sleep(5)

#增加 浏览器窗口最大化的操作是为了解决脚本偶尔不稳定的问题
driver.maximize_window()
id("btn_nologin").click()
time.sleep(3)

#如下步骤是在订单信息页面输入乘客姓名信息
css("#pasglistdiv > div > ul > li:nth-child(2) > input").send_keys("小刘")

基础常用方法代码如下：
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
