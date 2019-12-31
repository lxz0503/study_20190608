# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  13:55
# 文件名称   ：demo01.py
# 开发工具   ：PyCharm
word='编号   姓名       性别 年级      学校   奖项'
list=word.split(' ')
listnew=[i for i in list if i!='' ]
new=' '.join(listnew)
print(new)
