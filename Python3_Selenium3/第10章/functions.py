from datetime import datetime,date,timedelta
from selenium import webdriver
import xlrd
import logging

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

#这是新添加的函数，用于处理和获取Excel文件中的测试数据。
def read_excel(filename,index):
    xls = xlrd.open_workbook(filename)
    sheet = xls.sheet_by_index(index)
    #print(sheet.nrows)
    #print(sheet.ncols)
    dic={}
    for j in range(sheet.ncols):

        data=[]
        for i in range(sheet.nrows):
          data.append(sheet.row_values(i)[j])
        dic[j]=data
    return dic

def log(str):
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log-selenium.log',
                    filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.info(str)
