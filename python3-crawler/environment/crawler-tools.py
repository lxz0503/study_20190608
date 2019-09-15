import urllib
import urllib.request
import requests


with urllib.request.urlopen('https://www.baidu.com') as f:
    data = f.read()
    print('Status:', f.status, f.reason)
    print('Data:', data.decode('utf-8'))

result = requests.get('https://wwww.baidu.com')
print(result.status_code, result.reason)

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
db = client['xiaozhan']           # create datbase name is xiaozhan
db['performance'].insert({'name': 'tcp'})      # table is performance and insert values
r = db['performance'].find_one({'name': 'tcp'})   # use xiaozhan, show collections, db.performance.find().pretty()
print(r)