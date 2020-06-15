#! /usr/bin/env python3
# encoding=utf-8
from lxml.html import parse             # install lxml
from urllib.request import urlopen      # already install
import requests                         # install requests
from bs4 import BeautifulSoup           # install bs4
import time
import pandas as pd


url = 'https://bj.lianjia.com/ershoufang/'  # 设置URL的固定部分
page = 'pg'    # 设置页面可变部分
headers = {
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
    "Referer": "https://www.cnblogs.com"
}

for i in range(1, 3):
    if i == 1:
        i = str(i)   # change int i to string
        a = url+page+i+'/'
        r = requests.get(url=a, headers=headers)
        html = r.content
    else:
        i = str(i)
        a = url + page + i + '/'
        r = requests.get(url=a, headers=headers)
        html2 = r.content    # 第一页之外其他页面的内容
        html = html + html2        # 把所有页面内容拼接到一个html里面
    time.sleep(2)
# 用BeautifulSoup解析html页面
lj = BeautifulSoup(html, 'html.parser')
# 获取房源总价信息, 查找相关的div，再找对应的class
# price = lj.findAll('div', 'totalPrice')
price = lj.find_all('div', attrs={'class': 'totalPrice'})
tp = []
for a in price:
    totalPrice = a.span.string    # 定位到具体总价信息，结合网页来查看
    tp.append(totalPrice)
print(tp)

# 获取房源信息
houseInfo = lj.find_all('div', attrs={'class': 'houseInfo'})
hi = []
for b in houseInfo:
    house = b.get_text()    # 定位到具体总价信息，结合网页来查看
    hi.append(house)
for item in hi:
    print(item)

#

tagInfo = lj.find_all('div', attrs={'class': 'tag'})
tag_list = []
for b in tagInfo:
    tag_info = b.get_text()    # 定位到具体总价信息，结合网页来查看
    tag_list.append(tag_info)
for item in tag_list:
    print(item)

# 将数据导入pandas
house = pd.DataFrame({'totalPrice': tp, 'houseInfo': hi})
print(house.head())

#
house_info_list = pd.DataFrame((x.split('/') for x in house.houseInfo),
                               columns=['name', 'room', 'size', 'orientation', 'deco', 'elevator'])
# print(house_info_list.head())
# merge
house = pd.merge(house, house_info_list, right_index=True, left_index=True)
print(house)
print(house.iloc[:, 0].max())   #  ----?


