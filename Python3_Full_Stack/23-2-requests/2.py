#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/3/2022 3:44 PM
@file:2.py
@project:xiaozhan_git
"""
import requests

if __name__ == "__main__":
    url = 'https://fanyi.baidu.com/'
    # 发送带请求头的请求,这次伪装成了浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    data = {
        'from': 'en',
        'to': 'ch',
        'query': 'dictionary',   # this is a param,需要翻译的
        'simple_means_flag': '3',
        'sign': '763934.1002287',
        'token': '48377db13ec64e533d5a4d61b417b37f',    # 从首页获取
        'domain': 'common'
    }
    response = requests.post(url=url, headers=headers, data=data)
    print(len(response.content.decode()), response.content.decode())
    with open('baidufanyi.html', 'wb') as f:  # 字节形式写入文件
        f.write(response.content)
