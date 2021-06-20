#coding=utf-8
from urllib import request
import http.cookiejar
import urllib3
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
#消除SSL警告的信息
urllib6.disable_warnings()
#创建CookieJar对象
cookie = http.cookiejar.CookieJar()
opener = request.build_opener(request.HTTPCookieProcessor(cookie))
#在打开URL的过程中，会将cookie的信息存放至cookie对象中。
req = opener.open('http://sogou.com')
#遍历cookie对象
for i in cookie:
    print(i.name + ":"+ i.value)
