# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class QuoteItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 存储抓取网页的所有字段，可以理解为字典的key
    # text = scrapy.Field()
    # author = scrapy.Field()
    # tags = scrapy.Field()
    pass
    # 然后跳转到parse()方法去写解析方法
