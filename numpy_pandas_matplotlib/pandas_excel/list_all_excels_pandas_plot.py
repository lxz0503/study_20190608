# !/usr/bin/env python3
# coding=utf-8
import os
import pandas as pd
import time
import matplotlib.pyplot as plt


def click1():
    """find all excels under specific dir"""
    for root, dirnames, filenames in os.walk(os.path.dirname(__file__)):
        return [os.path.join(root, x).replace('\\', '/') for x in filenames if x.endswith('.xls')]
    # mylist = [x for x in os.listdir('.') if x.endswith('.xls')]


def clicked(mylist):
    """read all excels and merge them"""
    res = pd.read_excel(mylist[0])
    for i in range(1, len(mylist)):
        A = pd.read_excel(mylist[i])
        res = pd.concat([res, A], ignore_index=False, sort=True)  # 合并excel表格数据
    return res


def select_column(res):
    """show data in specific columns"""
    df1 = res[['买家会员名', '收货人姓名', '联系手机', '宝贝标题']]
    df2 = df1.loc[df1['宝贝标题'] == '零基础学Python']    # 只显示购买了这本书的信息
    return df2.head(10)


def sort_column(res):
    """分组算出每本书卖出的总数,reset_index()可以将分组结果转成DataFrame对象"""
    df1 = res.groupby(['宝贝标题'])['宝贝总数量'].sum().reset_index()
    df2 = df1.sort_values(by='宝贝总数量', ascending=False)
    return df2.head(10)


def select_column_plot(res):
    """plot销售收入占80%的统计"""
    df = res[(res.类别 == '全彩系列')]
    df1 = df.groupby(['图书编号'])['买家实际支付金额'].sum().reset_index()
    # save_df_to_excel(df1)
    print(df1)
    df1 = df1.set_index('图书编号')

    print(df1)
    df1 = df1['买家实际支付金额'].copy()   # copy seems can be removed
    print('df1', '--------', df1)
    df2 = df1.sort_values(ascending=False)
    print('df2', '-------', df2)
    # save_df_to_excel(df2)
    # plot
    plt.rc('font', family='SimHei', size=10)
    plt.figure('贡献度分析')
    df2.plot(kind='bar')
    plt.ylabel('销售收入')
    plt.xticks(rotation=0)
    # I can not understand below code,xiaozhan
    # p = 1.0*df2.cumsum()/df2.sum()
    # print('p', '-----', p)
    # p.plot(color='r', secondary_y=True, style='-o', linewidth=0.5)
    # plt.annotate(format(p[9], '.4%'), xy=(9, p[9]), xytext=(9*0.9, p[9]*0.9),
    #              arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.1'))
    # plt.ylabel('收入比例')
    plt.show()


def save_df_to_excel(df):
    """save data to excel"""
    file_name = time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.xlsx'
    writer = pd.ExcelWriter(file_name)
    df.to_excel(writer, 'xiaozhan', index=None)    # without index like 0 1 2 3 4
    writer.save()


if __name__ == '__main__':
    r1 = click1()
    r2 = clicked(r1)
    # r3 = sort_column(r2)
    # save_df_to_excel(r3)
    select_column_plot(r2)