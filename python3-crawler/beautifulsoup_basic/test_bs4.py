# coding=utf-8
from bs4 import BeautifulSoup
import requests
# demo中内容:
# <html><head><title>This is a python demo page</title></head>
# <body>
# <p class="title"><b>The demo python introduces several python courses.</b></p>
# <p class="course">Python is a wonderful general-purpose programming language. You can learn Python from novice to professional by tracking the following courses:
# <a href="http://www.icourse163.org/course/BIT-268001" class="py1" id="link1">Basic Python</a> and <a href="http://www.icourse163.org/course/BIT-1001870001" class="py2" id="link2">Advanced Python
# </a>.
# </p>
# <a href="http://www.icourse163.org/course/BIT-268002" class="py2" id="link2">Basic Java</a> and <a href="http://www.icourse163.org/course/BIT-1001870002" class="py3" id="link2">Advanced Java</a>.</p>
# </body></html>

result = requests.get('http://python123.io/ws/demo.html')
demo = result.text
print(demo)
# there are 3 types of parser: html.parser, lxml, xml
print('start to parser html')
soup = BeautifulSoup(demo, 'html.parser')
# soup = BeautifulSoup(demo, 'lxml')
# print(soup)
print('output with prettify():')
# print(soup.prettify())  # 格式化输出
#
print(soup.title)    # get title标签
print(soup.a)        # get第一个a标签信息
print(soup.a.name)
print(soup.a.parent.name)
print('第一个a标签的属性是:', soup.a.attrs)   # 字典格式 {'href': 'http://www.icourse163.org/course/BIT-268001', 'class': ['py1'], 'id': 'link1'}
print('a标签的href属性:', soup.a.attrs['href'])  # 通过字典的方式获取a标签的href属性
print('第一个a标签的内容是:', soup.a.string)  # a标签的非属性字符串信息，表示尖括号之间的那部分字符串
# find_all()可以用来查找标签元素，返回一个列表
print('所有a标签的内容:', soup.find_all('a'))           # 查找所有a标签
print('所有a标签的内容:', soup.find_all(['a', 'b']))    # 查找所有a和b标签
for t in soup.find_all('a'):   # for循环遍历所有a标签，并把返回列表中的内容赋给t
    print('t的值是:', t)       # 等价于soup.a
    print('a标签中的href属性:', t.get('href'))      # soup.a.attrs['href']
# 找到所有标签
for i in soup.find_all(True):
    print('标签名称:', i.name)

#
print('href属性为http..的a标签元素是:', soup.find_all('a', href='http://www.icourse163.org/course/BIT-268001'))
print('class属性为title的标签元素是：', soup.find_all(class_='title'))  # 指定属性，查找class属性为title的标签元素，注意因为class是python的关键字，所以这里需要加个下划线
print('id属性为link1的标签元素是：', soup.find_all(id='link1'))  # 查找id属性为link1的标签元素
#
print(soup.head)  # head标签
print(soup.head.contents)   # head标签的儿子标签，contents返回的是列表类型
# [<title>This is a python demo page</title>]
print(soup.body.contents)   # body标签的儿子标签
print(len(soup.body.contents))  # 获得body标签儿子节点的数量
print(soup.body.contents[3])   # 通过列表索引获取第一个节点的内容
#
print(type(soup.body.children))  # children返回的是一个迭代对象，只能通过for循环来使用，不能直接通过索引来读取其中的内容
for i in soup.body.children:   # 通过for循环遍历body标签的儿子节点
    print(i.name)   # 打印节点的名字
    # None
    # p
    # None
    # p
    # None