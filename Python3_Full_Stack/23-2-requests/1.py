#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/2/2022 3:15 PM
@file:查找重复值-图灵.py
@project:xiaozhan_git
"""
import requests

if __name__ == "__main__":
    url = 'http://www.baidu.com/'
    response = requests.get(url)
    response.encoding = 'utf-8'   # 为了显示页面的中文，必须对应编码 utf-8 or utf8
    # print(response.text)
    # print(res.content)    # 这是字节类型
    print(len(response.content.decode()),response.content.decode())   # 字符串类型
    # print(response.request.headers)   # 打印响应对应请求的请求头
    # 发送带请求头的请求,这次伪装成了浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    response1 = requests.get(url=url, headers=headers)
    print(response1.request.headers)
    print(len(response1.content.decode()), response1.content.decode())
    with open('baidu.html', 'wb') as f:   # 字节形式写入文件
        f.write(response1.content)

    # 在url携带参数   www.baidu.com/s?wd=python

    # 通过params携带字典参数
    url1 = 'http://www.baidu.com/s'
    data = {'wd': 'python3'}
    response2 = requests.get(url1, headers=headers, params=data)
    print(response2.content.decode())
    # write into html file
    with open('baidu2.html', 'wb') as f:   # 字节形式写入文件
        f.write(response2.content)

    # 在headers中设置cookies ---下面的代码没有成功，页面不全  暂时放弃
    url2 = 'https://jira.wrs.com/browse/WSTRPG-4?jql='
    headers1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Cookie': '_ga=GA1.2.1932129776.1655174038; ajs_user_id="b2ec30d07354c06cd4c2dcaea4c344c86bf5ca2c"; ajs_anonymous_id="3f2b1f3d-f0dd-40e6-8182-33be9988f7e6"; _gid=GA1.2.285289776.1662114525; JSESSIONID=6F36F7BCF1C79C336DC17A1FD7F82C0B; atlassian.xsrf.token=BWL4-5HLJ-GBHK-V1OT_14d38ae734412f2f56386e10155d032694f7ab39_lin'
    }

    # response3 = requests.get(url2, headers=headers1)
    # print(response3.content.decode())
    # write into html file
    # with open('jira.html', 'wb') as f:  # 字节形式写入文件
        # f.write(response3.content)

    # 将cookie字符串转换为cookies所需的字典格式
    # 用了字典推导式
    cookies_str = '_ga=GA1.2.1932129776.1655174038; ajs_user_id="b2ec30d07354c06cd4c2dcaea4c344c86bf5ca2c"'
    cookies_dict = {cookie.split('=')[0]:cookie.split('=')[1] for cookie in cookies_str.split(';')}
    print(cookies_dict)
    # {'_ga': 'GA1.2.1932129776.1655174038', ' ajs_user_id': '"b2ec30d07354c06cd4c2dcaea4c344c86bf5ca2c"'}

    # 请求头参数中携带cookie字典参数
    # resp = requests.get(url2, headers=headers, cookie=cookies_dict)

    # cookieJar对象转化为cookie字典
    response3 = requests.get(url=url, headers=headers)
    print(response3.cookies)
    cookies_dict = requests.utils.dict_from_cookiejar(response3.cookies)
    print(cookies_dict)

    # requests 代理设置
    proxies = {
        'http': 'http://1.1.1.1:9090',
        'https': 'https://1.1.1.1:80'
    }
    # response4 = requests.get(url=url, headers=headers, proxies=proxies)




