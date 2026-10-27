import time
import unittest
import HTMLTestRunner
from functions import date_n,id,css,xpath,js,return_driver,open_base_site
from functions import read_excel
from functions import log
from search_tickets import search_tickets

#以下代码为搜索火车票列表
#search_tickets("上海","杭州",1)
class booking_tickets(unittest.TestCase):
    def setUp(self):
        self.driver = return_driver()

    def test_ctrip_tickets(self):
        log("Read Excel Files to get test data.")
        dic1 = read_excel("testdata.xlsx",0)
        print(dic1[0][0],dic1[0][1])

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
    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(booking_tickets("test_ctrip_tickets"))
    file_name = "D:\\report_ctrip_tickets.html" #是为了设置生成的报表html文件地址。
    # fp = file(file_name,'wb')
    fp = open(file_name, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Test_Report_Portal', description='Report_Description') #此步是为了设置报表页面的title和报表总结描述内容。
    runner.run(suite)
    fp.close()
