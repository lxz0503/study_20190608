#! /usr/bin/env python3
# coding=utf-8
# WEB API需要经常和JSON字符串打交道
import requests
import json

def weather_report(city,low_temperature,highest_temperature,weather):
    '''输出天气'''
    output = '''
    {0}今日天气
    最低气温：{1}
    最高气温：{2}
    {3}
    '''
    print(output.format(city, low_temperature, highest_temperature, weather))

url = 'http://www.weather.com.cn/data/cityinfo/101010100.html'
response = requests.get(url)
response.encoding = "utf-8"

# 方式1：将JSON字符串转化为字典
weatherinfo = response.text      # JSON类型数据,本质也是字符串类型
# {"weatherinfo":{"city":"北京","cityid":"101010100","temp1":"18℃","temp2":"31℃","weather":"多云转阴","img1":"n1.gif","img2":"d2.gif","ptime":"18:00"}}
data = json.loads(weatherinfo)   # 转化为字典类型
# {'weatherinfo': {'city': '北京', 'cityid': '101010100', 'temp1': '18℃', 'temp2': '31℃', 'weather': '多云转阴', 'img1': 'n1.gif', 'img2': 'd2.gif', 'ptime': '18:00'}}
info = data['weatherinfo']
weather_report(info['city'], info['temp1'], info['temp2'], info['weather'])

# 方式2：直接返回字典类型
weatherinfo = response.json()
info = weatherinfo['weatherinfo']
weather_report(info['city'], info['temp1'], info['temp2'], info['weather'])





