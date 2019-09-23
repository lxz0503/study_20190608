# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
from pyquery import PyQuery as pq
import pymongo
from config_mongo import *


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]        # 创建了数据库

browser = webdriver.Chrome()
browser.get('https://www.taobao.com/')
wait = WebDriverWait(browser, 10, 0.2)

def search():
    try:
        input_box = wait.until(EC.presence_of_element_located((By.ID, 'q')))
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input_box.send_keys('美食')
        button.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_products()     # 页面信息出现后再调用此方法来解析页面
        return total.text
    except NoSuchElementException:
        print('no such element')
    except TimeoutException:
        print('timeout')
        return search()    # 超时的话就递归，继续等待
    finally:
        browser.quit()

def next_page(page_num):
    try:
        input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        # 等待直到标签按钮可点击为止
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input_box.clear()   # 首先情况输入框
        input_box.send_keys(page_num)
        button.click()
        # 查找高亮部分的数字是否是自己输入的数字
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), page_num))
        get_products()   # 翻页成功后查看页面信息
    except NoSuchElementException:
        print('no such element')
    except TimeoutException:
        print('timeout')
        return next_page(page_num)   # 超时就递归继续等待

def get_products():
    """
    解析美食图片页
    :return:
    """
    # 下面一句是定位到所有的美食图片
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source    # 获取当前网页的源代码
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()   # 返回一个迭代器,因为items下面有很多item
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('save data to mongodb successfully', result)
    except Exception as e:
        print('save data failed')
        print(e)

if __name__ == '__main__':
    res = search()
    # res = '共 100 页'
    total_page = int(re.compile('(\d+)').search(res).group(1))
    print(total_page)
    for i in range(2, total_page+1):
        next_page(i)
    browser.close()