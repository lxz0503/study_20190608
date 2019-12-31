# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  14:10
# 文件名称   ：demo02.py
# 开发工具   ：PyCharm
name=input('姓名：')
phone=input('电话：')
university=input('学校：')
data=name,phone,university
print(data )
print(' '.join(data) )
print(name,phone,university)
