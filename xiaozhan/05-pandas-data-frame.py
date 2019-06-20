import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = {'city': ['beijing', 'shanghai', 'shenzhen', 'guangzhou'],
        'year': [2016, 2017, 2018, 2019],
        'house_price': [50000, 48000, 35000, 30000]
        }    # 每一列数据, 通过字典来创建
# data_frame = pd.DataFrame(data, columns=['year', 'city', 'house_price'])
data_frame = pd.DataFrame.from_dict(data, orient='index',columns=['year', 'city', 'house_price','a'])
print(data_frame)
print(data_frame.values)
print(data_frame.get_values())  # 功能同上，获取所有数值
# print(data_frame.values[0])
# print(data_frame.values[0][2])
# print(data_frame.sort_values(by=['house_price'],na_position='first'))  # 依据house_price列排序，并将该列空值放在首位
# print(data_frame.sort_values(by=['city','house_price'],ascending=False))

x = pd.DataFrame({'x1':[1,2,2,3],'x2':[4,3,2,1],'x3':[3,2,4,1]})
# print(x)
# print(x.sort_values(by=0,ascending=False, axis=1)) # 按照索引值为0的行，即第一行的值来降序排序

# another example
frame = pd.DataFrame(np.arange(9).reshape(3, -1),  # -1 means generating columns automatically
                     index=['a', 'b', 'c'],   # 每行的名字
                     columns=['beijing', 'shanghai', 'hangzhou'] # 每列的名字
                     )
frame.plot.bar()
plt.show()
# print(frame)
print(frame.index[0])  # 打印第0行的index的名字
print(frame.columns[0]) # 打印第0列column的名字
# print(frame.ix['a':'b'])  # get value from index a to index b
# print(frame.sort_values(by=['beijing'],na_position='first'))
# print(frame[frame.beijing>0]) # get value from column beijing that are greater than 0

#
fileDf = pd.read_excel(r'F:\xiaozhan_git\study_20190608\xiaozhan\test_data.xlsx','Sheet1')
# print("check the info:")
# print(fileDf.head())
# print(fileDf.info())
# print(fileDf.describe())
# print(fileDf) # 打印所有内容
# print(fileDf['Baseline'].mean())  # 打印Baseline这一列的平均值
# print(fileDf['Baseline'].max())  # 打印Baseline这一列的最大值
# print(fileDf.fillna(value=5))

# print(fileDf.values)  # 打印每行的值，但是不包括column名字
# print(fileDf.values[1][1])
# print(fileDf['Baseline'] < 500)
# print(fileDf.head(3)) # 打印前3行
# print(fileDf[0:2]) # 用切片打印前两行数值
# print(fileDf.loc[1])
# print(fileDf.iloc[1])

# 修改数值
# 需要先用loc将数据提取出来，再赋值修改；
# 若需修改索引，可直接赋值df.index=##;
# 若需修改列名，可直接赋值df.columns=##
df = pd.DataFrame({'A': ['one', 'one', 'two', 'three']*3,
                   'B': ['A', 'B', 'C']*4,
                   'C': ['foo', 'foo', 'foo', 'bar', 'bar', 'bar']*2,
                   'D': np.random.randn(12),
                   'E': np.random.randint(0, 5, 12)
                   }
)
# print(df)
# 将A列为“one”，C列为“bar”的E列数据修改为110
df.loc[(df['A'] == 'one') & (df['C'] == 'bar'), 'E'] = 110
# print(df)
#修改索引为1-12
df.index=range(1, 13)
# print(df)

# pandas中索引的使用
data = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6], 'C': [7,8,9]}, index=["a","b","c"])
print(data)
# .loc[],中括号里面是先行后列，以逗号分割，行和列分别是行标签和列标签，比如我要得到数字5，那么就就是
print(data.loc['b', 'B'])
print(data.at['b','B']) # 只能定位单个元素，但是速度快
# 如果我要选择一个区域呢，比如我要选择5，8，6，9，那么可以这样做
# print(data.loc['b':'c', 'B':'C'])
# .iloc[]与loc一样，中括号里面也是先行后列，行列标签用逗号分割，与loc不同的之处是，.iloc 是根据行数与列数来索引的
# print(data.iloc[1, 1])
print(data.iat[1,1])  # 只能定位单个元素，但是速度快
# print(data.iloc[1:3, 1:3])
# .ix[]它既可以根据行列标签又可以根据行列数
# print(data.ix[1, 1])
# print(data.ix[1:3, 1:3])

#
df = pd.DataFrame({'AAA': [4, 5, 6, 7],
                   'BBB': [10, 20, 30, 40],
                   'CCC': [100, 50, -30, -50]}
                  )
df.loc[df.AAA >= 5, 'BBB'] = -1
print(df)
#    AAA  BBB  CCC
# 0    4   10  100
# 1    5   -1   50
# 2    6   -1  -30
# 3    7   -1  -50
df.loc[df.AAA >= 5, ['BBB', 'CCC']] = 555
print(df)
#    AAA  BBB  CCC
# 0    4   10  100
# 1    5  555  555
# 2    6  555  555
# 3    7  555  555
r = df.loc[(df.AAA <= 6) & (df.index.isin([0, 2, 3]))]
print(r)
#    AAA  BBB  CCC
# 0    4   10  100
# 2    6  555  555

fecha = pd.date_range('2012-4-10', '2015-1-4', periods=10)
print(fecha)
print(type(fecha))

# plot with data frame

speed = [0.1, 17.5, 40, 48, 52, 69, 88]
lifespan = [2, 8, 70, 1.5, 25, 12, 28]
index = ['snail', 'pig', 'elephant',
         'rabbit', 'giraffe', 'coyote', 'horse']
df = pd.DataFrame({'speed': speed, 'lifespan': lifespan}, index=index)
ax = df.plot.bar(rot=0, subplots=True)
plt.savefig(r"F:\xiaozhan_git\study_20190608\xiaozhan\dataframe_bar.jpg")
plt.show()

# example
# df = pd.DataFrame(np.random.randn(6, 4),
#                   index=['one', 'two', 'three', 'four', 'five', 'six'],
#                   columns=pd.Index(['A', 'B', 'C', 'D'], name='Genus')
#                   )
# print(df)
# df.plot.bar()
# plt.show()