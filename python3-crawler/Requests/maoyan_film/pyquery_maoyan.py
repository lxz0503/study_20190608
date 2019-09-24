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
    doc = pq(filename='maoyan_film.html')
    items = doc('#app > div > div > div > dl > dd').items()   #
    for item in items:
        product = {
            'image': item.find('a > img.poster-default').attr('src'),
            # 'title': item.find('div > div > div.movie-item-info > p.star').text(),
            # 'release_time': item.find('div > div > div.movie-item-info > p.releasetime').text().split(":")[-1],
            'score_integer': item.find('div > div > div.movie-item-number.score-num > p > i.integer').text(),
            'score_fraction': item.find('div > div > div.movie-item-number.score-num > p > i.fraction').text(),
        }
        print(product)
        # save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('save data to mongodb successfully', result)
    except Exception as e:
        print('save data failed')
        print(e)

if __name__ == '__main__':
    get_products()
