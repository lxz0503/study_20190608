#!/usr/bin/env python3
# coding=utf-8
import pandas as pd
from pyecharts.charts import Bar
from pyecharts import options as opts

# 创建一个柱状图Bar实例,read data from excel
class Html_Bar(object):
    def __init__(self, excel_path, sheet_name, html_name):
        self.excel_path = excel_path
        self.sheet_name = sheet_name
        self.html_name = html_name
        self.df = self.read_data

    @property
    def read_data(self):
        return pd.read_excel(self.excel_path, self.sheet_name)

    @property
    def bar_chart(self):
        bar = (
            Bar()
            # 添加X轴数据
            .add_xaxis(self.df['length'].to_list())
            # 添加Y轴数据,系列的名称,根据需要可以添加多个y轴数据
            .add_yaxis("SR0610", self.df['SR0610'].to_list())
            .add_yaxis("SR0620", self.df['SR0620'].to_list())
            .add_yaxis("SR0630", self.df['SR0630'].to_list())
            # 添加标题
            .set_global_opts(title_opts=opts.TitleOpts(title="主标题: release performance", subtitle="副标题:performance"))
        )
        return bar

    def html_bar(self):
        return self.bar_chart.render('Bar-High-Low.html')


if __name__ == '__main__':
    ts = Html_Bar('release_data.xls', sheet_name='ARM', html_name='Bar-High-Low.html')
    ts.html_bar()
    # 输出保存为图片
    # make_snapshot(snapshot, res.render(), "003_Options配置项_自定义样式_保存图片.png")