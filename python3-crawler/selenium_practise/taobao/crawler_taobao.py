# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
from config_mongo import *


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]        #


def get_products():
    doc = pq(filename='taobao_meishi.html')
    items = doc('#mainsrp-itemlist .items .item').items()   #
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        # print(product)
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('save data to mongodb successfully', result)
    except Exception as e:
        print('save data failed')
        print(e)

if __name__ == '__main__':
    get_products()
