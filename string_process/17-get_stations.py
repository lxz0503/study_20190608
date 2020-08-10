#!/usr/bin/env python3
# coding=utf-8

import re
import requests


def write_stations(stations, file_name):
    with open(file_name, 'w', encoding='utf_8_sig') as f:
        f.write(stations)

def read_stations(file_name):
    with open(file_name, 'r', encoding='utf_8_sig') as f:
        data = f.readline()    # read only one line
    return data

def get_selling_time():
    url = 'https://www.12306.cn/index/script/core/common/qss_v10082.js'
    res = requests.get(url)
    res = res.text
    res = res.strip('var citys =')     # 由于返回的不是标准的JSON格式文本，所以直接用strip去掉了开头的内容
    print(type(res))   # str
    print(type(eval(res)))   # dict
    ret = eval(res)
    write_stations(res, 'time.txt')

def query_time(station):
    url = 'https://www.12306.cn/index/otn/index12306/queryScSname'
    # form 参数
    form_data = {"station_telecode": station}
    res = requests.post(url, data=form_data)
    res.encoding = 'utf-8'
    json_data = res.json()    # change to dict
    data = json_data['data']
    print(data)

if __name__ == '__main__':
    test = """天津|TJP|重庆|CQW|aaa.com"""
    stations = re.findall(r'([\u4e00-\u9fa5]+)\|([A-Z]+)', test)   # 这个正则表达式可以匹配前面是中文，然后|,后面是英文的字符串
    print(stations)  # [('天津', 'TJP'), ('重庆', 'CQW')]
    stations = dict(stations)
    print(stations)  # {'天津': 'TJP', '重庆': 'CQW'}
    stations = str(stations)   # {'天津': 'TJP', '重庆': 'CQW'}
    print(stations)
    write_stations(stations, 'stations.txt')
    #
    stations = read_stations('stations.txt')
    print(type(stations))   # this is str
    stations = eval(read_stations('stations.txt'))   # use eval to change to dict
    print(type(stations), stations)   # this is dict
    from_stations = list(stations.keys())
    print(from_stations)     # ['天津', '重庆']
    from_stations = list(stations.values())
    print(from_stations)     # ['TJP', 'CQW']
    #
    get_selling_time()
    with open('time.txt', encoding='utf_8_sig') as f:   # 如果文本里有中文，就用utf_8_sig来解码
        res = f.read()
    print(res)

    #
    station = 'BJP'
    query_time(station)