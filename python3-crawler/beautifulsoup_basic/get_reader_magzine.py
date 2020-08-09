"""This can get reader magazine"""
# !/usr/bin/env python3
# coding=utf-8

import requests
import time
from bs4 import BeautifulSoup

def get_time():
    cur_time = str(time.localtime().tm_year) + '-' + str(time.localtime().tm_mon) + '-' + str(time.localtime().tm_mday)
    return cur_time

def url_to_soup(url):
    res = requests.get(url)
    html = res.text
    # 创建BeautifulSoup对象，它可以从html或者xml中提取数据
    soup = BeautifulSoup(html, 'html.parser')
    ret = soup.find_all('a')
    return ret

if __name__ == '__main__':
    ret = get_time()
    print(ret)
    ret = url_to_soup('http://python123.io/ws/demo.html')
    print(ret)