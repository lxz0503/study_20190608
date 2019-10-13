# -*- coding: utf-8 -*-
import scrapy
# from quotetutorial.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']   # 可以写多个URL

    def parse(self, response):
        quotes = response.css('div.quote')         # 语法借鉴了pyquery
        for quote in quotes:
            # item = QuoteItem()
            # text = quote.css('span.text::text').get()   # 如果只有一条内容，就用get()
            # author = quote.css('small.author::text').get()
            # tags = quote.css('div.tags a.tag::text').getall()     # 有多个tag，所以就用getall()
            # item['text'] = text
            # item['author'] = author
            # item['tags'] = tags
            # yield item
            # print(dict(text=text, author=author, tags=tags))
    # 爬虫会产出很多字典类型数据，所以用yield
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall()
            }

    # get next page
        next_page = response.css('li.next a::attr(href)').get()   # 学习这种语法
        if next_page is not None:    # response.follow()允许使用相对路径
            yield response.follow(next_page, callback=self.parse)    # 相当于一个递归调用,callback是一个回调函数

