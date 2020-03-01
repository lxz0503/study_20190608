#!/usr/bin/env python3
# coding=utf-8
from pyecharts.charts import Line
from pyecharts import options as opts
from datetime import datetime

# 导入输出图片工具
from pyecharts.render import make_snapshot
# 使用snapshot-selenium 渲染图片
from snapshot_selenium import snapshot


# 创建一个折线图Line实例
def line_chart(series_nightly, series_baseline, nightly, baseline, title):
    line = (
        Line()
            # 添加X轴数据
            .add_xaxis(["TCP_64", "UDP_1400", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            # 添加Y轴数据,系列的名称,根据需要可以添加多个y轴数据
            # .add_yaxis("Baseline", [5, 20, 36, 10, 75, 90])
            # .add_yaxis("Nightly", [8, 15, 60, 20, 25, 30])
            .add_yaxis(series_name=series_nightly, y_axis=nightly)
            .add_yaxis(series_name=series_baseline, y_axis=baseline)
            # 添加标题
            .set_global_opts(title_opts=opts.TitleOpts(title=title, subtitle="副标题:服饰类"))
    )
    return line


if __name__ == '__main__':
    series_nightly = 'Nightly'
    series_baseline = 'Baseline'
    nightly_data = [8, 15, 60, 20, 25, 30]
    baseline_data = [5, 20, 36, 10, 75, 90]
    title = '{:test result on %Y-%m-%d}'.format(datetime.now())
    res = line_chart(series_nightly, series_baseline, nightly_data, baseline_data, title)
    res.render('simple-line.html')
    # 输出保存为图片
    # make_snapshot(snapshot, res.render(), "003_Options配置项_自定义样式_保存图片.png")