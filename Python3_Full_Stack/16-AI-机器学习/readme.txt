全部代码都是用jupyter notebook来打开运行
对应视频的源代码是 05--人工智能经典算法

以练习为主
matplotlib绘图流程：
创建画布
绘制图像
显示图像
--------------
matplotlib 3层结构：
容器层：canvas  figure  axes
辅助显示层： 添加x轴 y轴 标题
图像层： 绘制什么图像的声明

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

plt.savefig('a.png')
plt.show()    先保存，然后show，否则先show的话资源就释放了


x = range(60)
y = [random.uniform(10,15) for i in x]    取60个随机数，介于10到15之间

random.uniform(a,b) #用于生成一个指定范围内的随机浮点数,两个参数其中一个是上限,一个是下限

-----------------------
http://c.biancheng.net/matplotlib/subplots.html    学习链接
视频 16-3-3  matplotlib   基本画图的使用
x_ticks_labels ----一个列表，如果设置这个，就会在x y 轴显示

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import random

x = range(60)
y = [random.uniform(10,15) for i in x]

#  画布
plt.figure(figsize=(20,8),dpi=100)
plt.plot(x,y)

#  构造x轴刻度显示的名字
y_ticks = range(40)
# x_ticks_labels = ['11:{}'.format(i) for i in x]

# 添加x y 轴刻度  第一个参数必须是数字，一般
plt.yticks(y_ticks[::5])
# plt.xticks(x[::5],x_ticks_labels[::5])
plt.xticks(x[::5])
# 添加网格
plt.grid(True)
plt.show()
-------------------------------------------------
视频  16-3-3-18  多层次plot 显示图例
jupyter notebook中显示中文： https://blog.csdn.net/weixin_42513469/article/details/113179134
# 显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

1. 下载simhei.ttf字体，这里提供一个链接SimHei.ttf
2. 找到你的解释器的fonts文件夹下的ttf文件夹，例如我的解释器是Anaconda，在Anaconda的安装目录下，fonts文件夹的位置如上图的路径：D:\AnaInstallDir\Anaconda3\Lib\site-packages\ matplotlib\mpl-data\fonts\ttf。
若解释器是自己安装的Python，文件夹的位置一般为：
C:\Users\用户名\AppData\Local\Programs\ Python\ Python35\Lib\site-packages\matplotlib\mpl-data\fonts\ttf
3. 将下载的SimHei.ttf文件放入ttf文件夹下再运行程序就OK啦（即代码plt.rcParams[‘font.sans-serif’] = [‘SimHei’]可以运行）
————————————————
版权声明：本文为CSDN博主「lsp—vip」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/weixin_42513469/article/details/113179134

如果同时画多个折线图，需要增加显示图例来区分不同折线 plt.legend()
画图时候要同时设置label选项

视频 16-3-3-19  多个坐标系显示图像
视频 16-3-3-20 折线图的应用场景
视频 16-4-4  Numpy
3维数组 简单理解为 一个[]里面包含多个 [[1,2,3],[2,3,4]],
例如：
c= array([[[1,2,3],[2,3,4]],  [[3,4,5],[4,5,6]]])
array([[[1, 2, 3],
        [2, 3, 4]],

       [[4, 5, 6],
        [5, 6, 7]]])

c.shape = (2,2,3)  ---第一个2代表有两大块，第二个2代表每一块有两行，3代表每行有3个元素
上面三个数字可以去定位多维数组中的元素   参见视频 16-4-4-7
--------------------------------------------------------------
2维数组可以理解为  一个[]里面包含多个  [1,2,3],[2,3,4]
c = np.array([[1,2,3],  [2,3,4]])
---------------------------------------------------------------------
视频 16-4-4-5  生成0或者1的数组
np.zeros([3,4])    --二维数组， 3*4列
np.ones([3,4])

创建darray的时候可以指定 np.dtype=np.float64 或者  np.string_  默认是int64

深拷贝---不改变原来的内容---相当于挪到其他地方--再修改后和原来的内容就无关了
浅拷贝----相当于创建快捷方式---修改的话会关联原来的内容
np.linspace(1,100,10)  --从1到100等间隔生成10个数   包括100
np.linspace(a,b,c)用于创建一个等差序列的向量，向量值是[a,b]之间均匀分布的c个实数

np.arange(10,50,2)    # 不包括50
np.logspace(0,2,3)   # 10的2次方生成3个数
----------------------------------------------------------------------
视频 16-4-4-6  正态分布
均值 --- 决定图形的左右位置
方差 ---- 决定图像的胖瘦
方差越小---图形越瘦高  数据越集中
方差越大----图形越矮胖  数据越分散

视频 16-4-4-7   切片和形状参数
二维数组切片：
stock_change[0:2,0:3]    # 前两行 前三列

stock_change[0,0,0]  第一个元素，
stock_change[0,0,1]  第二个元素，

a1[1,0,0],a1[1,0,1],a1[1,0,2]   # 三个数字维度的意义  第一大块，第一行 第一个元素，依此类推

数组里面索引是 先行后列  ----记住

视频 16-4-4-8 类型修改和数组去重

视频 16-4-4-9  ndarry的运算
使用random.normal()方法获取正态数据分布。
它具有三个参数：

loc-（平均）钟声峰值所在的位置。
scale-（标准偏差）图形分布的平坦程度。
size-返回数组的形状。

np.all(stock_change>0)  全部大于0才返回True
np.any(stock_change>0)   只要有一个大于0就返回True

视频 16-4-4-10  矩阵的概念    xiaozhan  需要复习线性代数 才能理解一些矩阵运算
矩阵乘法  M行*N列 乘以 N行*L列 = M行*L列的矩阵

数组与数组的运算-----先理解概念
数组+1---代表数组每个元素都加1  以此类推其他运算 加减乘除

两个数组进行运算的前提： xiaozhan  慢慢理解 看例子
维度相同 例如都是3*3
shape(其中相对应的一个地方为1)
例如3*3*3 + 1*1*3
np.dot(a,10)  也支持矩阵和数字相乘
注意那个求加权平均值的例子----实际中比较实用  xiaozhan

Numpy中存储的是ndarray   即多维数组   适合科学计算
折线图  看变化
散点图  看分布
直方图  hist  看统计分布
Numpy底层使用了C语言，释放了GIL 即全局解释器锁

视频 16-5-5-  pandas  重点学习
从视频13开始  pandas介绍
pd.DataFrame()  注意第一个参数的格式，参考以前写的例子  有多种格式参数可以传递  例如 字典 列表等
pandas中行索引 是axis=0    列索引 是 axis=1
创建日期索引  pd.date_range()
修改行列索引值  必须全部修改 不能只修改其中某行或者某列  ----xiaozhan
如果重设索引  即恢复到原始状态  0 1 2 3这种 用函数  stock_c.reset_index(drop=True)

pandas设置某一列作为索引：
df.set_index('列名')
pd.read_csv('文件名',index_col=0)  第0列作为索引

# 下面的代码表示取消行索引 缺失值标记为 数据缺失
data.to_csv("out.csv",encoding = 'utf_8_sig',index = False,na_rep = '数据缺失')

# 将数据保存至zip压缩文件
# 如果想保留中文  就添加参数 encoding='utf_8_sig'
compression_opts = dict(method='zip',
                        archive_name='out.csv')
data.to_csv('out.zip', index=False,encoding='utf_8_sig',
          compression=compression_opts)

将之前数据转换为 markdown 形式表格，这样可以直接复制进 .md 文件中使用：
data.head().to_markdown(index = None)

# 将之前的数据保存为 html 格式至当前目录下（文件名任意），并进行如下设置
取消行索引
标题居中对齐
列宽100
encoding='utf_8_sig'  xiaozhan这个表示显示中文
data.to_html("out.html",encoding='utf_8_sig',col_space=100,index = None,justify = 'center',border = 1)

# 将dataframe数据转换为markdown  然后能直接拷贝到.md后缀的文件
需要安装 pip3 install tabulate
df = data.head().to_markdown(index=None)

视频 16-5-5-2  索引操作  获取数据
用到文件stock_data.csv   先读取
自定义运算函数  就是应用apply(func,axis=0或者1)
如果jupyter notebook里面提示没有定义，但是明明在前面的cell定义了
这时候需要重新执行一下最前面定义变量部分的代码即可   相当于重新导一下

缺失值处理  type(np.NaN) ---float类型
如果缺失值不是NaN,先全部替换为NaN,然后再进行缺失值处理 ----例如认为 []是缺失值
但是null这种默认就是缺失值  就不用替换
df.replace(to_place='?', value=np.nan)

指定缺失值：
用字典来解决这个问题。如果na_values的参数是一个字典，那就可以为具体的列来指定缺失值的样子。
我们就可以指定在Age这一列，0要被看成缺失值；在Comment这一列，“该用户没有评价”被看成缺失值。代码如下：
df = pd.read_csv('test.csv',na_values={'age':0, 'city':'NA'})
上面的代码表明 在age列，0就是缺失值，在city那一列，NA是缺失值
这样处理后，再去读取 这些缺失值就会显示为NaN---就能做缺失值处理

pd.read_csv('某招聘网站数据.csv',na_values=['[]'])  ---将[]标识为缺失值
pd.read_csv('某招聘网站数据.csv',na_values=['[]','数据分析']).head()  ---指定多个缺失值

不处理缺失值： pd.read_csv("某招聘网站数据.csv",na_filter=False).head()

pandas读取各种文件的介绍：https://www.cnblogs.com/lavender1221/p/12695811.html
分块读取数据，参考下面的链接：
https://blog.csdn.net/weixin_43790560/article/details/88587123

pandas读取hdf5文件----数据处理中最常用  大数据存储    xiaozhan  不熟悉这种
https://zhuanlan.zhihu.com/p/104145585

https://www.cjavapy.com/article/2713/    各种编程函数介绍

16-5-5-13  数据离散化
简单理解为把连续的数据 划分为不同的区间来处理
pd.qcut(data_p,10)  默认区间
pd.cut(data_p,bins=bins)   自定义区间
cut_r = pd.cut(data_p,bins=bins)
cut_r.value_counts()    # 查看每个区间多少数据

哑变量  热独编码 即把数据变成 0 1 形式来存储 pd.get_dummies()
一行一样本，一列一特征
16-5-5-14  数据合并
交叉表可以显示统计数据
数据透视表可以显示比例
一般都是显示两列的关系

在对numpy数组求平均np.mean()或者求数组中最大最小值np.max()/np.min()时，
如果数组中有nan,此时求得的结果为：nan，那么该如何忽略其中的nan呢？

此时应该用另一个方法    即都以nan开头的方法

np.nanmean(),np.nanmax(),np.nanmin()

[j for i in temp_list for j in i]    # 嵌套列表表达式
上面的循环嵌套列表  先执行 for i in temp_list---拿到了i的值
然后执行 for j in i ---拿到了j的值


-------------------------------
https://blog.csdn.net/m0_72662900/article/details/125758772

tuple和list转成numpy的array数据类型
my_list = [1,2,3]
my_array = np.array(my_list)
===========================================================
在用python绘制一个时间序列的柱状图时，由于时间年份较多，准备筛选一些年份进行绘制。
pandas读取特定的行或者列   奇数或者偶数行 列
如果index为数值形式，采用df = df [df.index%2==0]选择偶数行，或者是等于1选择奇数行。
如果index不是数值类型，采用df = df[[i%2==0 for i in range(len(df.index))]]构建数组选择偶数行所在的下标。
如果是选择列，则采用df=df.iloc[:,[i%2==0 for i in range(len(df.columns))]]的方式进行选择。

loc或者iloc的用法 参考链接：
https://blog.csdn.net/weixin_38037405/article/details/121211411
data = pd.read_csv("某招聘网站数据.csv",chunksize=10)
# data
for chunk in data:   # 每个chunk都是一个DataFrame 类型
#     print(chunk)
    for i in range(len(chunk)):
#         print(chunk.iloc[i]['positionId'])
#         print(chunk.loc[:,['positionId','createTime']])   # 选取多行或者多列  用loc
        print(chunk.loc[0:3,['positionId']])  读取0-3行 包括3，也就是4行

作者：王叽叽的小心情
链接：https://www.jianshu.com/p/5f4bd01bf291
来源：简书
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
======================================
视频 16-6-6-3  K近邻算法
一行就是一个样本   一列就是一个特征
参考判断电影类型那个例子   比较容易理解

16-6-6-4  K近邻算法的初步使用

scikit-learn工具  必须掌握  专门用于机器学习的库  算法已经封装---省事 但是简单了解一下
pip3 install scikit-learn
import sklearn
print(sklearn.__version__)
1.1.2

from sklearn.neighbors import KNeighborsClassifier
KNeighborsClassifier(n_neighbors=5)

16-6-6-5   距离度量

标准差是方差的算术平方根
标准差=方差的算术平方根=s=sqrt(((x1-x)^2+(x2-x)^2+......(xn-x)^2)/n)

圆周角等于所对的圆心角的一半
圆内接四边形对角互补

=========================================================================
如何查找缺失值所在的行：

步骤1：使用isnull()返回是否是缺失值。
isnull()会对DataFrame中的每个元素进行缺失值检查，若为缺失值返回True；不是缺失值返回False；
最终返回一个DataFrame.
miss = drink.isnull()

步骤2：找到存在缺失值的行。使用any，并设定axis=1，则当每一行中存在缺失值时就会返回True；
若需要找到所有缺失值都为True的行则使用all即可。
miss.any(axis=1)

步骤3：通过步骤1、2即可得到存在缺失值的行索引
drink[miss.any(axis=1)==True].head(3)

========================================================
#用上一行的数数据填充
df_ffill = df.fillna(method = 'ffill')

#用下一行的数数据填充
df_bfill = df.fillna(method = 'bfill')

==============================================
pandas数据的格式化
https://blog.csdn.net/Triumph19/article/details/125581521
https://zhuanlan.zhihu.com/p/553665592
df['A1'].apply(lambda x:format(x,'.2f')) ## '.2f'表示保留2位小数
df['A1'].apply(lambda x:format(x,'.2%')) ## '.2%'表示转化为百分数后，保留2位小数
==================================================
有条件删除某行数据：drop函数里面参数是行index
df.drop(df[df.金牌数<20].index)
注意： df[df.金牌数<20].index  返回一个列表

# 通过列号提取数据
df.iloc[:,[0,1,2,3]].head()
# 通过列名提取  用到函数 df.loc
df.loc[:,['金牌数','银牌数','铜牌数']].head()
#
df.loc[字符串]  里面的参数表示行索引名字

# 下面是通过行列索引名字来定位
df.loc[['viper', 'sidewinder'], ['shield']] = 50

提取 中国、美国、英国、日本、巴西 五行数据
df.loc[df['国家奥委会'].isin(['中国','美国','英国','日本','巴西'])]

提取 0-50 行，间隔为 3
df[:50:3]
df[行index] 里面参数是行index
df[字符串]  里面的字符串代表着列名

# 找出前10行里面金牌数大于30的数据
# df.loc[:10,:].loc[df['金牌数']>30]
df.iloc[:10,:].loc[df['金牌数']>30]

# 下面两个条件需要用小括号括起来
df.loc[(df['国家奥委会'].isin(['中国','美国','英国','日本','巴西'])) & (df['金牌数'] < 30)]

提取第 4 行，第 4 列的值：
df.iloc[3][3]

# 提取 国家奥委会 为 中国 的金牌数
# df[df['国家奥委会']=='中国']['金牌数'] # 方法1

df.loc[df['国家奥委会']=='中国'].loc[1].at['金牌数']  # 学习这种方法  比较繁琐
df.loc[df['国家奥委会']=='中国'].loc[1].at['排名']   # 提取国家奥委会为中国的奖牌排名

query函数用法  https://blog.csdn.net/weixin_42596342/article/details/120303484
# 使用 query 提取 金牌数 大于 金牌均值的国家
gold_mean = df['金牌数'].mean()
df.query(f'金牌数 > {gold_mean}')

=================================



#画图步骤
1.导入matplotlib包及其相关包
2.准备数据，numpy数组
3.绘制原始曲线
4.添加标题，坐标轴，刻度，图例（图例的参考case09，不要看视频，视频是错的）
5.添加文字说明，注释
6.显示，保存绘图结果