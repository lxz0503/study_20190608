#!/usr/bin/env python3
# coding=utf-8
from pyecharts.charts import Bar
from pyecharts import options as opts
from datetime import datetime

# 导入输出图片工具
from pyecharts.render import make_snapshot
# 使用snapshot-selenium 渲染图片
from snapshot_selenium import snapshot

# 创建一个柱状图Bar实例
def bar_chart():
    bar = (
        Bar()
        # 添加X轴数据
        .add_xaxis(["TCP_64", "UDP_1400", "雪纺衫", "裤子", "高跟鞋", "袜子"])
        # 添加Y轴数据,系列的名称,根据需要可以添加多个y轴数据
        .add_yaxis("Baseline", [5, 20, 36, 10, 75, 90])
        .add_yaxis("Nightly", [8, 15, 60, 20, 25, 30])
        # 添加标题
        .set_global_opts(title_opts=opts.TitleOpts(title="主标题: 双十一销量", subtitle="副标题:服饰类"))
    )
    return bar


if __name__ == '__main__':
    res = bar_chart()
    res.render('Bar-High-Low.html')
    # 输出保存为图片
    # make_snapshot(snapshot, res.render(), "003_Options配置项_自定义样式_保存图片.png")
