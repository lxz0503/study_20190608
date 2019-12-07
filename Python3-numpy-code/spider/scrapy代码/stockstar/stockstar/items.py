# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class StockstarItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class StockstarItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    code = scrapy.Field()  # 股票代码
    abbr = scrapy.Field()  # 股票简称
    last_trade = scrapy.Field()  # 最新价
    chg_ratio = scrapy.Field()   # 涨跌幅
    chg_amt = scrapy.Field()     # 涨跌额
    chg_ratio_5min = scrapy.Field() # 5分钟涨幅
    volumn = scrapy.Field()  # 成交量
    turn_over = scrapy.Field()  # 成交额