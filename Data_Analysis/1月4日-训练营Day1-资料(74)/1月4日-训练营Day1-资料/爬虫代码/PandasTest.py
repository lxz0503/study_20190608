import pandas as pd
from pandas import Series,DataFrame
x1 = Series([1,2,3,4])
x2 = Series(data=[1,2,3,4],index=['a','b','c','d'])
mydata = {'a':1,'b':2,'c':3,'d':4}
x3 = Series(mydata)
# print(x1)
# print(x2)
# print(x3)
#
# print(x3.count())
# print(x3.max())
# print(x3.min())
# print(x3.mean())
# print(x3.sum())
# print(x3.median())
# print(x3.argmax())
# print(x3.var())
# print(x3.describe())

df1 = DataFrame({'name':['zhangfei','guanyu','a','b','c'],'data1':range(1,6)})
df2 = DataFrame({'name':['zhangfei','guanyu','A','B','C'],'data2':range(1,6)})
df3 = pd.merge(df1,df2,on='name')
print(df1)
print(df2)
print(df3)

df3 = pd.merge(df1,df2,how='inner')
print(df3)

df3 = pd.merge(df1,df2,how='left')
print(df3)
df3 = pd.merge(df1,df2,how='right')
print(df3)
df3 = pd.merge(df1,df2,how='outer')
print(df3)

data = {'Chinese': [66, 95, 93, 90,80], 'Math': [30, 98, 96, 77, 90], 'English': [65, 85, 92, 88, 90]}
df = DataFrame(data, index=['ZhangFei', 'GuanYu', 'LiuBei', 'DianWei', 'XuChu'], columns=['Chinese', 'Math', 'English'])

print(df)
print(df.loc['ZhangFei'])
print(df.iloc[0])
print(df.columns)
print(df.iloc[2]['Math'])
print(df.iloc[2]['Chinese'])
