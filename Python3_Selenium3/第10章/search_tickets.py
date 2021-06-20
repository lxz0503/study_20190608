'''
此页面是为了测试火车票查询的页面元素的功能。
'''
from selenium.webdriver.common.action_chains import ActionChains
from functions import date_n,id,css,xpath,js,return_driver,open_base_site
#from selenium import webdriver
import time

'''
函数名： search_tickets
参数：
 from_station: 出发站
 to_station: 到达站
 n： 是一个数字，如1表示选择明天的车票，2表示选择后天的车票。
'''

def search_tickets(from_station,to_station,n):
    driver =return_driver()
    open_base_site("https://trains.ctrip.com/TrainBooking/SearchTrain.aspx")
    #from_station = "上海"
    from_station = from_station
    #to_station = "杭州"
    to_station = to_station

    #以下为tomorrow变量
    tomorrow = date_n(n)

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
测试代码文件test_booking_tickets.py如下。
import time
from functions import date_n,id,css,xpath,js,return_driver,open_base_site
from functions import read_excel
from functions import log
from search_tickets import search_tickets

#以下代码为搜索火车票列表
#search_tickets("上海","杭州",1)
log("Read Excel Files to get test data.")
dic1 = read_excel("testdata.xlsx",0)
log("Begin to search tickets")
search_tickets(dic1[0][0],dic1[0][1],1)
log("End to search tickets")
log("Begin to get driver object.")
driver = return_driver()

#在页面跳转时最好是加一些时间等待的步骤，免得有一些元素定位的异常出现。
time.sleep(2)

#在车次K1805车次的硬座区域点击预定按钮，来预定车票,
#此处为了代码的健壮，需要用到xpath＋模拟查询来增强测试代码
log("Click book button :)")
xpath("//div[starts-with(@id,'tbody-01-K1805')]/div[1]/div[6]/div[1]/a").click()

#如下步骤是为了实现不用登录到携程系统而实现订票的目的。
time.sleep(5)

#增加 浏览器窗口最大化的操作是为了解决脚本偶尔不稳定的问题
driver.maximize_window()
id("btn_nologin").click()
time.sleep(3)

#如下步骤是在订单信息页面输入乘客姓名信息
#css("#pasglistdiv > div > ul > li:nth-child(2) > input").send_keys("小刘")
log("input order information")
css("#pasglistdiv > div > ul > li:nth-child(2) > input").send_keys(dic1[0][2])
