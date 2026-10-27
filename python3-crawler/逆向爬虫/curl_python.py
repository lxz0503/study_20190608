#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:10/10/2022 11:40 AM
@file:curl_python.py
@project:xiaozhan_git
"""
import requests

params = {
    'tn': 'sitehao123_15',
}

response = requests.get('https://www.baidu.com/', params=params)
print(response.content.decode())
