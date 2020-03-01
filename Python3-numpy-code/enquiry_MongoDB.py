#!/usr/bin/env python3
# encoding=utf-8

import pymongo


def search_mongo():
    client = pymongo.MongoClient('localhost', 27017)      # create a connection to MongoDB
    book_weather = client['weather']      # database name is weather
    sheet_weather = book_weather['sheet_weather_3']     # table name is sheet_weather_3
    # 查找键值为HeWeather5.basic.city为背景的数据
    # for item in sheet_weather.find({'HeWeather5.0.basic.city': '北京'}):
    for item in sheet_weather.find():    # 会打印出所有数据
        # print(item)
    # 查询每个城市3天的天气预报，所以循环3次，查看JSON节点结构
        for i in range(3):
            tmp = item['HeWeather5'][0]['daily_forecast'][i]['tmp']['min']  # 找到当天的最低气温，是字符串类型
            # update方法可以修改数据，修改为数值类型
            sheet_weather.update_one({'_id': item['_id']},
                                     {'$set': {'HeWeather5.0.daily_forecast.{}.tmp.min'.format(i): int(tmp)}})
    # 提取气温低于5度的城市
    for item in sheet_weather.find({'HeWeather5.0.daily_forecast.tmp.min': {'$gt': 5}}):
        print(item['HeWeather5'][0]['basic']['city'])




if __name__ == '__main__':
    search_mongo()

# 在MonggoDB里面查询数据的关键是找到对应的节点，可以用在线工具查看JSON数据的节点格式，
# 也可以在pycharm里面直接打开MongoDB数据库，查看每条数据，就能看到存储格式，包括字段类型
# 例如本例子中HeWeather5是每条数据里面的独立节点，然后在它的下面还有其他节点
# 如果查找它下面的节点，可以越过其中某些节点，例如添加0和不添加0这个节点，结果一样
