#!/usr/bin/env python3
# coding=utf-8
# this is drawing a pie chart

import json
from pyecharts.charts import Bar
from pyecharts import options as opts


f = open('pies.json')
data = json.load(f)
name = data['name']
sales = data['sales']
sales_volume = data['sales_volume']


bar = (Bar()
           .add_xaxis(name)
           .add_yaxis('sale', sales)
     .set_global_opts(title_opts=opts.TitleOpts(title="主标题", subtitle="副标题"))
       )

bar.render('pie1.html')