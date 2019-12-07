#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/3 13:08
# @Author  : Fairy Huang
# @File    : main.py

from scrapy.cmdline import execute

execute(["scrapy", "crawl", "stock", "-o", "items.json"])