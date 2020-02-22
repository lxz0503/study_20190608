# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  16:42
# 文件名称   ：demo04.py
# 开发工具   ：PyCharm

name = '王李张李陈王杨张吴周王刘赵黄吴杨'
name_len = len(name)        # 字符串下标总长度
for s in name:
    if name[0] in name[1:name_len]:
        name = name[1:name_len]
    else:
        name = name[1:name_len] + name[0]
print(name)









