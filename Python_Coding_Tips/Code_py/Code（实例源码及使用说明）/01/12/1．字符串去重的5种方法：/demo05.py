# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  16:46
# 文件名称   ：demo05.py
# 开发工具   ：PyCharm
name = '王李张李陈王杨张吴周王刘赵黄吴杨'
# zd = {}.fromkeys(name)  # 字典的key是不能重复的
# print(zd)     # {'王': None, '李': None, '张': None, '陈': None, '杨': None, '吴': None, '周': None, '刘': None, '赵': None, '黄': None}
# mylist = list(zd.keys())
mylist = list({}.fromkeys(name).keys())
print(''.join(mylist))
