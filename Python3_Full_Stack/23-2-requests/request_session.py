#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/3/2022 5:10 PM
@file:request_session.py
@project:xiaozhan_git
"""
import requests
import re

def login():
    # session
    session = requests.session()
    # headers
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    # url1获取token
    url1 = 'https://github.com/login'
    # 获取网页内容
    res1 = session.get(url1).content.decode()
    # 正则提取内容
    token = re.findall('name="authentication_token" value="(.*?)" />', res1)

    # url2 登录github
    url2 = 'https://github.com/session'
    # 构建表单数据  ---可以直接拷贝网页中的Form Data部分
    data = {
        "commit": "Sign int",
        "utf8": "yes",
        "authenticity_token": token,    # xiaozhan 
        "login": "username",
        "password": "bbbb"
    }
    # 发送请求登录
    session.post(url2,data=data)

    # url3点击 set profile
    url3 = 'https://github.com/username'
    response = session.get(url3)
    #
    with open('github.html', 'wb') as f:
        f.write(response.content)
    
    
if __name__ == "__main__":
    pass
