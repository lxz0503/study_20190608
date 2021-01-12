# from pyecharts.charts import Bar
# bar = Bar()
# bar.add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
# bar.add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
# # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
# # 也可以传入路径参数，如 bar.render("mycharts.html")
# # 也可以将图形在jupyter中输出，如
# # bar.render_notebook()
# bar.render()

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map
df = pd.read_excel('./国内疫情.xlsx',sheet_name = '2020-07-04')
# 1. 根据绘制国内总疫情图(确诊)
data = df.groupby(by='province',as_index = False).sum()
data_list = list(zip(data['province'].values.tolist(),data['confirm'].values.tolist())) # ------------中国地图
def map_china() -> Map:
    c=(
    Map()
    .add(series_name="确诊病例", data_pair=data_list, maptype="china") .set_global_opts(
    title_opts=opts.TitleOpts(title="疫情地图"), visualmap_opts=opts.VisualMapOpts(is_piecewise=True,
                  pieces=[{"max": 9, "min": 0, "label": "0-9","color":"#FFE4E1"},
                      {"max": 99, "min": 10, "label": "10-99","color":"#FF7F50"},
                      {"max": 499, "min": 100, "label": "100-499","color":"#F08080"},
                      {"max": 999, "min": 500, "label": "500-999","color":"#CD5C5C"},
                      {"max": 9999, "min": 1000, "label": "1000-9999",
    "color":"#990000"},
                      {"max": 99999, "min": 10000, "label": ">=10000",
    "color":"#660000"}]
                           )
    ) )

    return c
d_map = map_china()
# d_map.render_notebook()
d_map.render('疫情.html')