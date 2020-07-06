import pandas as pd
aa = '../data/mingribooks.xls'
df = pd.DataFrame(pd.read_excel(aa))
df1 = df.groupby(["宝贝标题"])["宝贝总数量"].sum()
print(df1.head(3))
# df1.to_excel('dict.xls')     # 列名分别为: 宝贝标题 宝贝总数量

mydict = df1.to_dict()
print(mydict)
# 遍历字典
for item in mydict.items():     # 以tuple的方式显示字典key-value
    print(item)
