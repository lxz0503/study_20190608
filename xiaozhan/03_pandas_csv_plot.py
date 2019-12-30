import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.ticker as ticker
import os

# 读取CSV数据为numpy record array记录

f_dir = os.path.dirname(__file__) + '/bug_record.csv'
r = mlab._csv2rec(f_dir)
# r.sort()
print(r)
# 形成Y轴坐标数组
N = len(r)
ind = np.arange(N)  # the evenly spaced plot indices
# ind1这里是为了把图撑大一点
ind1 = np.arange(N+3)

# 将X轴格式化为日期形式，X轴默认为0.5步进，
# 这里将整数X轴坐标格式化为日期，.5的不对应日期，
# 因为扩展了3格坐标，所以N+的坐标点也不显示日期
def format_date(x, pos=None):
    if not x%1 and  x<N:
        thisind = np.clip(int(x), 0, N-1)
        return r.create_date[thisind].strftime('%Y-%m-%d')
    else:
        return ''

# 绘图
fig = plt.figure()
ax = fig.add_subplot(111)
# 下行为了将图扩大一点，用白色线隐藏显示
ax.plot(ind1,ind1,'-',color='white')
# 正常要显示的bug总数折线
ax.plot(ind, r['all'], 'o-',label='All of BUGs')
# 正常要显示的bug已解决总数折线
ax.plot(ind, r['resolved'], 'o-',label='Resolved BUGs')
# 正常要显示的bug已关闭总数折线
ax.plot(ind, r['closed'], 'o-',label='Closed BUGs')
# 图标的标题
ax.set_title(u"BUG Trend Chart")
# 线型示意说明
ax.legend(loc='upper left')

# 在折线图上标记数据，-+0.3是为了错开一点显示数据
datadotxy=tuple(zip(ind-0.3, r['all']+0.3))
for dotxy in datadotxy:
    ax.annotate(str(int(dotxy[1]-0.3)),xy=dotxy)

datadotxy=tuple(zip(ind-0.3, r['resolved']+0.3))
for dotxy in datadotxy:
    ax.annotate(str(int(dotxy[1]-0.3)),xy=dotxy)

datadotxy=tuple(zip(ind-0.3, r['closed']+0.3))
for dotxy in datadotxy:
    ax.annotate(str(int(dotxy[1]-0.3)),xy=dotxy)

#将X轴格式化为日期形式
ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
fig.autofmt_xdate()

#显示图片
plt.show()

#将图片保存到指定目录
# plt.savefig(r"D:\xiaozhan_git\study_20190608\xiaozhan\csv.jpg")

# 作者：jtscript
# 来源：CSDN
# 原文：https://blog.csdn.net/jtscript/article/details/44928535
# 版权声明：本文为博主原创文章，转载请附上博文链接！