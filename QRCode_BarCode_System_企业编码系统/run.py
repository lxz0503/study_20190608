#!/usr/bin/env python3
# coding=utf-8

import os, time, string, random, tkinter, qrcode
import tkinter.filedialog
import tkinter.messagebox
from tkinter import *
from string import digits
from util import *

# root = tkinter.Tk()

allis = '1234567890ABCDEFGHHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+'
# i = 0

fourth = []
fifth = []

randsec = ''
randthr = ''
str_one = ''
strtwo = ''
nextcard = ''
userput = ''
nres_letter = ''


def mainmenu():
    print(
        """\033[1;35m
        ****************************************************************
                                企业编码生成系统
        ****************************************************************
        1.生成6位数字防伪编码（213563型）
        2.生成9位系列产品数字防伪编码（879-335439型）
        3.生成25位产品序列号（B2R12-N7TE-9IET2-FE350-DW2K4）
        4.生成含数据分析功能的防伪编码（5A6M0583D2）
        5.智能批量生成带数据分析功能的防伪码
        6.后续补加生成防伪码
        7.EAN-13条形码批量生成
        8.二维码批量输出
        9.企业粉丝防伪码抽奖
        0.退出系统
        ================================================================
                          说明：通过数字键选择菜单
        ================================================================
        \033[0m""")
    #
    i = 0
    while i <= 9:
        # mainmenu()
        choice = input('\033[1;32m  请输入您要选择的菜单选项：\033[0m')
        if len(choice) != 0:
            if choice == '1':
                scode1(str(choice))
            if choice == '2':
                scode2(choice)
            if choice == '3':
                scode3(choice)
            if choice == '4':
                scode4(choice)
            if choice == '5':
                scode5(choice)
            if choice == '6':
                scode6(choice)
            if choice == '7':
                scode7(choice)
            if choice == '8':
                scode8(choice)
            if choice == '9':
                scode9(choice)
            if choice == '0':
                i = 0
                print('正在退出系统！')
                break
        else:
            print('\033[1;31;40m   输入非法，重新输入！\033[0m')
            time.sleep(2)


if __name__ == '__main__':
    mainmenu()

