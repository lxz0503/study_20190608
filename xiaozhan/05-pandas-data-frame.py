import pandas as pd
import numpy as np

data = {'city': ['beijing', 'shanghai', 'shenzhen', 'guangzhou'],
        'year': [2016, 2017, 2018, 2019],
        'house_price': [50000, 48000, 35000, 30000]
        }    # 每一列数据, 通过字典来创建
data_frame = pd.DataFrame(data, columns=['city', 'year', 'house_price'])
print(data_frame)
# print(data_frame.values)
print("the row number is %s" % len(data_frame))
print("the column size is %s" % data_frame.columns.size)
print(data_frame.columns)
for index in data_frame.index:
    print(data_frame.loc[index].values[:])

for index, row in data_frame.iterrows():
    # print(type(data_frame.values[index]))
    # print(data_frame.values[index])
    print(row['city'], row['year'], row['house_price'])
# for row in data_frame.itertuples():
#     for index, colu in data_frame.iteritems():
#
#         print(getattr(row, 'city'), getattr(row, 'year'), getattr(row, 'house_price'))
        # print(getattr(row, index))
# print(data_frame.values[0][2])
# print(data_frame.sort_values(by=['house_price'],na_position='first'))  # 依据house_price列排序，并将该列空值放在首位
# print(data_frame.sort_values(by=['city','house_price'],ascending=False))

x = pd.DataFrame({'x1': [1, 2, 2, 3], 'x2': [4, 3, 2, 1], 'x3': [3, 2, 4, 1]})
# print(x)
# print(x.sort_values(by=0,ascending=False, axis=1)) # 按照索引值为0的行，即第一行的值来降序排序

# another example
frame = pd.DataFrame(np.arange(9).reshape(3, -1),  # -1 means generating columns automatically
                     index=['a', 'b', 'c'],   # 每行的名字
                     columns=['beijing', 'shanghai', 'hangzhou'] # 每列的名字
                     )
# print(frame)
# print(frame.ix['a':'b'])  # get value from index a to index b
# print(frame.sort_values(by=['beijing'],na_position='first'))
# print(frame[frame.beijing>0]) # get value from column beijing that are greater than 0

#
# fileDf = pd.read_excel(r'F:\xiaozhan_git\study_20190608\xiaozhan\test_data.xlsx', 'Sheet1')
fileDf = pd.read_excel(r'D:\xiaozhan_git\study_20190608\xiaozhan\test_data.xlsx', 'Sheet1')
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
data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]}, index=["a", "b", "c"])
print(data)
# 遍历
for index, row in data.iterrows():
    #print(index)
    print(row)
# .loc[],中括号里面是先行后列，以逗号分割，行和列分别是行标签和列标签，比如我要得到数字5，那么就就是
print(data.loc['b', 'B'])
print(data.at['b', 'B'])   # 只能定位单个元素，但是速度快
# 如果我要选择一个区域呢，比如我要选择5，8，6，9，那么可以这样做
# print(data.loc['b':'c', 'B':'C'])
# .iloc[]与loc一样，中括号里面也是先行后列，行列标签用逗号分割，与loc不同的之处是，.iloc 是根据行数与列数来索引的
# print(data.iloc[1, 1])
print(data.iat[1, 1])  # 只能定位单个元素，但是速度快
# print(data.iloc[1:3, 1:3])
# .ix[]它既可以根据行列标签又可以根据行列数
# print(data.ix[1, 1])
# print(data.ix[1:3, 1:3])

fecha = pd.date_range('2012-4-10', '2015-1-4', periods=10)
print(fecha)
print(type(fecha))
