# -*- coding: utf-8 -*-
import scrapy


class CnblogshomespiderSpider(scrapy.Spider):
    name = 'CnblogsHomeSpider'
    allowed_domains = ['cnblogs.com']
    start_urls = ['http://cnblogs.com/']

    def parse(self, response):
        print(response.text)
        pass
