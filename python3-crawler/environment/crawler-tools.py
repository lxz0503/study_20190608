import urllib
import urllib.request
import requests



result = requests.get('https://wwww.baidu.com')
print(result.status_code, result.reason)
# print(result.text)    # this can get the web content
# print(result.headers)    # this can get request headers, it is a dictionary
print(result.request)     # this is a get request
print(result.url)      #

#
from lxml import etree

html = etree.parse('test.html', etree.HTMLParser())
result = etree.tostring(html, encoding='gbk')   # parse to bytes
print(type(html))
print(type(result))
print(result.decode('gbk'))
#
from bs4 import BeautifulSoup

f = open('data.html')
soup = BeautifulSoup(f, 'lxml')
print(soup.head) #
f.close()

# https://pythonhosted.org/pyquery/api.html
from pyquery import PyQuery as pq

doc = pq(url='https://www.cnblogs.com/zhangxinqi/p/9219476.html')
print('the type of doc is', type(doc))
print(doc('p').text())

#
import pymongo

client = pymongo.MongoClient('localhost')
db = client['xiaozhan']           # create database name is xiaozhan
insert_data = {"board": "board_name", "TCP": 64}
myquery = {"board": "IA"}
# db['performance']    this is to create a table
# db['performance'].insert(insert_data)
db['performance'].insert({'name': 'tcp'})      # table is performance and insert values,the value is a dictionary
# r = db['performance'].find_one({'name': 'tcp'})   # use xiaozhan, show collections, db.performance.find().pretty()
r = db['performance'].find_one(myquery)   # use xiaozhan,

print(r)
# db.sheet_weather_3.findOne()
# db.sheet_weather_3.find({'HeWeather5.basic.city': '北京'})
#
# import redis
# r = redis.Redis('localhost', 6379)
# r.set('name', 'bob')
# result = r.get('name')
# print(result)

#!/usr/bin/python3

# import pymongo

# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# mydb = myclient["runoobdb"]
# mycol = mydb["sites"]

mylist = [
    {"name": "Taobao", "alexa": "100", "url": "https://www.taobao.com"},
    {"name": "QQ", "alexa": "101", "url": "https://www.qq.com"},
    {"name": "Facebook", "alexa": "10", "url": "https://www.facebook.com"},
    {"name": "??", "alexa": "103", "url": "https://www.zhihu.com"},
    {"name": "Github", "alexa": "109", "url": "https://www.github.com"}
]

mycol.insert_many(mylist)
