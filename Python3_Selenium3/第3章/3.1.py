###
###配套视频已出版，学习有疑问联系作者qq:2574674466###
###
#引入python自带的os代码模块
import os 
#导入WebDriver模块
from selenium import webdriver
#设置IE浏览器的WebDriver驱动程序路径
IEDriverServer="C:\\Program Files (x86)\\Internet Explorer\\IEDriverServer.exe"
#设置当前os webdriver为IE浏览器的驱动程序
os.environ["webdriver.ie.driver"] = IEDriverServer
#启动IE浏览器
driver =  webdriver.Ie(IEDriverServer) 
#打开百度首页
driver.get('https://www.baidu.com')


#chrome

from selenium import webdriver
#这里需要制定真实的Chrome浏览器驱动路径
ChromeDriverServer="C:\\Users\\xxx\\chromedriver.exe"
driver = webdriver.Chrome(ChromeDriverServer)
driver.get('https://www.baidu.com')

