# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  16:56
# 文件名称   ：demo04.py
# 开发工具   ：PyCharm
city = ['上海', '广州', '上海', '成都', '上海', '上海', '北京', '上海', '广州', '北京', '上海']
city.sort(reverse=True)
print(city)    # 排序后的列表
for x in city:
    while city.count(x) > 1:
        del city[city.index(x)]
print(city)
