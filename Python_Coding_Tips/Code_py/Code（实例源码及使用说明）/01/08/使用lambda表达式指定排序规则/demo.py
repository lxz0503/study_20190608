# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  13:26
# 文件名称   ：demo01.py
# 开发工具   ：PyCharm
list_dict = [{"name": "无语", "python": 99, "c": 89},
            {"name": "wgh", "python": 100, "c": 80},
            {"name": "琦琦", "python": 95, "c": 97},
            {"name": "明日", "python": 91, "c": 96}]

print("对列表排序前：")
for d in list_dict:
    print(d)
list_dict.sort(key=lambda x: x['python'], reverse=True)  # 降序排列

print("对列表排序后：")
for d in list_dict:
    print(d)
