# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  16:23
# 文件名称   ：demo02.py
# 开发工具   ：PyCharm

name='王李张李陈王杨张吴周王刘赵黄吴杨'
newname=''
i = len(name)-1
while True:
    if i >=0:
        if name[i] not in newname:
            newname+=(name[i])
        i-=1
    else:
        break
print (newname)
