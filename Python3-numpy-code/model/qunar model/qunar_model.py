########################################################################
#                                                                      #
#        去哪儿网 旅游天数、酒店评分、酒店等级 vs 路线价格 建模        #
#                                                                      #
########################################################################
#%matplotlib inline
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm


df = pd.read_csv("D:/qunar_routes.csv")
print (df.head())
print (df.info())

df["天数"]=df.路线信息.str.extract('(\d+)天\d+晚').apply(lambda x: int(x))
df["酒店评分"]=df.酒店信息.str.extract('(\d\.\d)分').apply(lambda x: float(x))
df["酒店等级"]=df.酒店信息.str.extract('\n(.*)')
df["价格"]=df.路线信息.str.extract('(\d+)起/人').apply(lambda x: int(x))
print (df.head())
print (df.info())

class_map = {"其他":0,"经济型":1,"舒适型":2,"高档型":3,"豪华型":4}
df["酒店等级"]=df["酒店等级"].map(class_map)

# 对变量画直方图，查看是否有异常值
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
df["酒店等级"].plot(ax=axes[0], kind='hist', title="酒店等级")
df["酒店评分"].plot(ax=axes[1], kind='hist', title="酒店评分")
df["价格"].plot(ax=axes[2], kind='hist', title="价格")

#提取自变量X,因变量y
X,y = df.ix[:,4:-1].values, df.ix[:,-1].values

# 拟合OLS线性回归模型 
ols = sm.OLS(y,X)
result = ols.fit()
print (result.summary())

y_pred = result.predict(X)
ratio = y_pred/y
df["性价比"] = ratio
print (df.sort_values("性价比", ascending=False))