# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import json

class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):     # 这个是关键函数，一定要实现
        if 'inspirational' in item['tags']:    # 自己添加的判断条件，可以去掉，只是练习用
            line = json.dumps(dict(item)) + "\n"    # 把字典类型数据转成json
            self.file.write(line)                   # 写到一个json文件
        return item                             # 必须返回item


class MongoPipeline(object):    # 把所有爬取的数据写入MongoDB数据库
    collection_name = 'items'     # table name

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):     # 很关键，重点
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')    # 去setting.py里面获取数据
        )

    def open_spider(self, spider):    # mongodb相关的初始化
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert(dict(item))   # 往MongoDB里面写入数据
        return item                # 必须返回item
