# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  16:49
# 文件名称   ：demo01.py
# 开发工具   ：PyCharm

city = ['上海', '广州', '上海', '成都', '上海', '上海', '北京', '上海', '广州', '北京', '上海']
ncity = []
for item in city:
    if item not in ncity:
        ncity.append(item)
print(ncity)
