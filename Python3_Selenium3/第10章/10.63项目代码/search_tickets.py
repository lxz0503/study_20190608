'''
此页面是为了测试火车票查询的页面元素的功能。
'''
from functions import date_n,id,css,xpath,js,return_driver,open_base_site,click_blank
import time

'''
函数名： search_tickets
参数：
 from_station: 出发站
 to_station: 到达站
 n： 是一个数字，如1表示选择明天的车票，2表示选择后天的车票。
'''
def search_tickets(from_station,to_station,n):
    #driver =return_driver()
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

    #ActionChains(driver).move_by_offset(0,0).click().perform()
    click_blank()

    #以下为点击车次搜索按钮
    id("searchbtn").click()
