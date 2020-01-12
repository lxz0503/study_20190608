#!/usr/bin/env python3
# coding=utf-8
# 抓取天气预报，实现用时访问的策略，即用迭代器，而不是简单的for,避免了占用大量内存，显示慢
# for循环的本质就是先生成一个迭代对象，然后不断地调用next()
# 下面的例子网站，点击后会自动下载一个文件，Json格式，用r.json()转换为python的字典格式
# 要求：从网站抓取需要的城市气温信息，并依次显示；
# 问题：如果一次抓取所有城市天气再显示，显示第一个城市气温时，有很高的延时，并且浪费存储空间；
# 期望从‘用时访问’的策略，并且能把所有城市气温装到一个对象里，可用for语句进行迭代。如何实现？
#
# 方案：
# 实现一个迭代器对象WeatherIterator，next方法每次返回一个城市气温；
# 实现一个可迭代对象WeatherIteratble，__iter__方法返回一个迭代器对象；
import requests
from collections import Iterator,Iterable

class WeatherIterator(Iterator):
    def __init__(self, cities):
        self.cities = cities
        self.index = 0

    def get_weather(self, city):
        r = requests.get(u'http://wthrcdn.etouch.cn/weather_mini?city=' + city)
        data = r.json()['data']['forecast'][0]
        return '%s: %s, %s' % (city, data['low'], data['high'])
    # [u'北京',u'上海', u'广州', u'长春']
    #     print(get_weather(u'北京'))
    def __next__(self):
        # 用if语句刻画最终迭代完后的状况；self.index，刻画迭代的位置
        if self.index == len(self.cities):   # 迭代的结束条件必须有，否则就是死循环
            raise StopIteration
        # 正常迭代情况，即每次迭代出一个城市的气温信息；self.cities[self.index]，得到需要的城市名字
        city = self.cities[self.index]
        self.index += 1
        return self.get_weather(city)


# 实现可迭代对象，继承Iterable，则对WeatherIterable实例化时，需要传入一个可迭代的对象；
class WeatherIterable(Iterable):
    def __init__(self, cities):
        self.cities = cities
    # 可迭代接口，在其内部返回WeatherIterator

    def __iter__(self):
        # 报错：Can't instantiate abstract class WeatherIterator with abstract methods __next__，
        # 即：不能用抽象的方法实例化抽象类WeatherIterator ——— 将next方法改为__next__()方法；
        return WeatherIterator(self.cities)


# test case
for x in WeatherIterable([u'北京', u'上海', u'广州', u'长春']):
    print(x)



