###
###配套视频已出版，学习有疑问联系作者qq:2574674466###
###
#coding=utf-8
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from thred_unit.basic_case import ParaCase
from thred_unit.basic_case import DetailCase
import  threading,unittest

#本例通过selenium server并发操作
#继承父类threading.Thread
class myThread (threading.Thread):   
    def __init__(self, device):
        threading.Thread.__init__(self)
        self.device=device

    def run(self):
        print ("Starting " + self.name)
        print ("Exiting " + self.name)
        run_suite(self.device)

def run_suite(device):
    suite = unittest.TestSuite()
    suite.addTest(ParaCase.parametrize(DetailCase, param=device))
    unittest.TextTestRunner(verbosity=1).run(suite)
if __name__ == '__main__':
url = 'http://127.0.0.1:4444/wd/hub'
browser = [DesiredCapabilities.CHROME,DesiredCapabilities.FIREFOX]
for i in range(len(browser)):
    th= myThread(webdriver.Remote(command_executor=url,desired_capabilities=browser[i]))
    th.start()
    th.join()
