#!/usr/bin/env python3
# coding=utf-8
from pyecharts.charts import Line
from pyecharts import options as opts
import pandas as pd
from datetime import datetime

# 导入输出图片工具
from pyecharts.render import make_snapshot
# 使用snapshot-selenium 渲染图片
from snapshot_selenium import snapshot


# 创建一个折线图Line实例
class Html_Line(object):
    def __init__(self, excel_path, sheet_name, html_name):
        self.excel_path = excel_path
        self.sheet_name = sheet_name
        self.html_name = html_name
        self.df = self.read_data
        self.run_date = 'test result on {:%Y-%m-%d}'.format(datetime.now())

    @property
    def read_data(self):
        return pd.read_excel(self.excel_path, self.sheet_name)

    @property
    def line_chart(self):
        line = (
            Line()
            # 添加X轴数据
            .add_xaxis(self.df['length'].to_list())
            # 添加Y轴数据,系列的名称,根据需要可以添加多个y轴数据
            .add_yaxis("SR0610", self.df['SR0610'].to_list())     # 第一个参数是column名字
            .add_yaxis("SR0620", self.df['SR0620'].to_list())
            .add_yaxis("SR0630", self.df['SR0630'].to_list())
            # 添加标题
            .set_global_opts(title_opts=opts.TitleOpts(title="主标题: release performance", subtitle=self.run_date))
        )
        return line

    def html_line(self):
        return self.line_chart.render('Line-High-Low.html')


if __name__ == '__main__':
    ts = Html_Line('release_data.xls', sheet_name='ARM', html_name='Line-High-Low.html')
    ts.html_line()
    # 输出保存为图片
    # make_snapshot(snapshot, res.render(), "003_Options配置项_自定义样式_保存图片.png")