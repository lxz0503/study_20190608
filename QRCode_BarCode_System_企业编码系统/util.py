#!/usr/bin/env python3
# coding=utf-8
import os
import tkinter.messagebox
import tkinter.filedialog
from tkinter import *
import random
import string

randstr = []
number = '1234567890'
letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
# randfir = ''
# root = tkinter.Tk()

def mk_dir(file_path):   # create dir
    if not os.path.exists(file_path):
        os.mkdir(file_path)


def openfile(filename):    # open file and read content
    with open(filename) as f:
        r = f.read()
    return r


def inputbox(showstr, showorder, length):
    instr = input(showstr)      # showstr is the indication of input information
    if len(instr) != 0:
        # 1：要求输入数字，不限位数； 2：字母；  3：数字且有位数要求
        if showorder == 1:
            if str.isdigit(instr):    # 判断输入是否是数字
                if instr == '0':
                    print('\033[1;31;40m 输入为0，请重新输入！\033[0m')
                    return '0'  # why
                else:
                    return instr
            else:
                print('\033[1;31;40m 输入非法，请重新输入！\033[0m')
                return '0'

        if showorder == 2:   # 输入是字母且指定长度
            if str.isalpha(instr):    # 判断输入是否是字母, 字母位数由length决定
                if len(instr) != length:
                    print('\033[1;31;40m必须输入' + str(length) + '个字母,请重新输入！\033[0m')
                    return '0'
                else:
                    return instr
            else:
                print('\033[1;31;40m 输入非法，请重新输入！\033[0m')
                return '0'

        if showorder == 3:   # 输入数字且指定位数
            if str.isdigit(instr):
                if len(instr) != length:
                    print('\033[1;31;40m必须输入' + str(length) + '个数字,请重新输入！\033[0m')
                    return '0'
                else:
                    return instr
            else:
                print('\033[1;31;40m 输入非法，请重新输入！\033[0m')
                return '0'

    else:
        print('\033[1;31;40m输入为空，请重新输入！\033[0m')
        return '0'     # why

# 保存防伪码，打印输出
def wfile(sstr, sfile, typeis, smsg, datapath):
    root = tkinter.Tk()
    mk_dir(datapath)
    datafile = datapath + '/' + sfile
    with open(datafile, 'w') as f:
        wrlist = sstr    # 传过来的参数是一个列表
        pdata = ''
        wdata = ''
        for i in range(len(wrlist)):
            print(wrlist[i])
            wdata = str(wrlist[i].replace('[', '').replace(']', ''))  # remove []
            wdata = wdata.replace('""', '').replace('""', '')  # remove ""
            f.write(str(wdata))
            pdata = pdata + wdata
    print('\033[1;31m' + pdata + '\033[0m')  # print to screen
    if typeis != 'no':
        tkinter.messagebox.showinfo('提示', smsg + str(len(wrlist)) + '\n 防伪码文件存放位置： ' + datafile)
        # root = tkinter.Tk()
        root.withdraw()


def scode1(choice):    # 生成6位防伪码
    incount = inputbox('\033[1;32m  请输入要生成的防伪码数量：\033[0m', 1, 0)
    while int(incount) == 0:
        incount = inputbox('\033[1;32m  请输入要生成的防伪码数量：\033[0m', 1, 0)
    randstr.clear()
    for j in range(int(incount)):
        randfir = ''
        for i in range(6):
            randfir = randfir + random.choice(number)
        randfir = randfir + '\n'
        randstr.append(randfir)
    #
    wfile(randstr, 'scode' + str(choice) + '.txt', '', '生成6位防伪码共计：', 'codepath')


def scode2(choice):    # 生成多个产品系列的9位防伪码
    ordstart = inputbox('\033[1;32m 请输入产品系列号（3位数字）：\033[0m', 3, 3)
    while int(ordstart) == 0:
        ordstart = inputbox('\033[1;32m 请输入产品系列号（3位数字）：\033[0m', 3, 3)
    ordcount = inputbox('\033[1;32m 请输入产品系列的数量：\033[0m', 1, 0)
    while int(ordcount) < 1 or int(ordcount) > 9999:
        ordcount = inputbox('\033[1;32m 请输入产品系列的数量：\033[0m', 1, 0)
    incount = inputbox('\033[1;32m 请输入每个系列的产品的防伪码数量：\033[0m', 1, 0)
    while int(incount) == 0:
        incount = inputbox('\033[1;32m 请输入每个系列的产品的防伪码数量：\033[0m', 1, 0)
    randstr.clear()
    for m in range(int(ordcount)):      # 有多少个系列产品
        for j in range(int(incount)):   # 每个系列产品有多少防伪码
            randfir = ''
            for i in range(6):
                randfir = randfir + random.choice(number)  # 每次生成一个随机数
            randstr.append(str(int(ordstart) + m) + randfir + '\n')
    wfile(randstr, 'scode' + str(choice) + '.txt', '', '已经生成9位防伪码共计：', 'codepath')


def scode3(choice):  # 生成25位产品防伪序列码
    incount = inputbox('\033[1;32m  请输入要生成的25位混合产品序列号数量： \033[0m', 1, 0)
    while int(incount) == 0:
        incount = inputbox('\033[1;32m  请输入要生成的25位混合产品序列号数量： \033[0m', 1, 0)
    randstr.clear()
    for j in range(int(incount)):
        strone = ''
        for i in range(25):
            strone = strone + random.choice(letter)   # strone是25位字母
        strtwo = strone[:5] + '-' + strone[5:10] + '-' + strone[10:15] + '-' + \
                     strone[15:20] + '-' + strone[20:25] + '\n'
        randstr.append(strtwo)

    wfile(randstr, 'scode' + str(choice) + '.txt', '', '25位防伪序列码：', 'codepath')


def scode4(choice):   # 9位防伪码中间插入3个字母
    intype = inputbox('\033[1;32m  请输入数据分析编号（3位字母）： \033[0m', 2, 3)
    while not str.isalpha(intype) or len(intype) != 3:
        intype = inputbox('\033[1;32m  请输入数据分析编号（3位字母）： \033[0m', 2, 3)
    incount = inputbox('\033[1;32m  输入带数据分析的防伪码数量：\033[0m', 1, 0)
    while int(incount) == 0:
        incount = inputbox('\033[1;32m  输入带数据分析的防伪码数量：\033[0m', 1, 0)
    ffcode(incount, intype, 'no', choice)

# 将数据分析码随机插入到9位防伪码中
def ffcode(scount, typestr, ismessage, choice):
    randstr.clear()
    for j in range(int(scount)):
        strpro = typestr[0].upper()
        strtype = typestr[1].upper()
        strclass = typestr[2].upper()
        randfir = random.sample(number, 3)   # 随机抽取3个位置,返回一个list
        randsec = sorted(randfir)
        letterone = ''
        for i in range(9):
            letterone = letterone + random.choice(number)
        # 将3个字母按照randsec中存储的位置值添加到9位数字防伪码中,切片原理，自己画一下草图就知道了
            sim = str(letterone[0:int(randsec[0])]) + strpro + \
              str(letterone[int(randsec[0]):int(randsec[1])]) + strtype + \
              str(letterone[int(randsec[1]): int(randsec[2])]) + strclass + \
              str(letterone[int(randsec[2]):]) + '\n'
        randstr.append(sim)
    wfile(randstr, typestr + 'scode' + str(choice) + '.txt', ismessage, '生成含数据分析功能的防伪码：', 'codepath')

# 自动生成多个产品系列，是scode4的扩展
def scode5(choice):
    default_dir = 'codeauto.txt'
    # file_path = tkinter.filedialog.askopenfilename()
    with open(default_dir) as f:
        r = f.read().split('\n')
        for item in r:
            codea = item.split(',')[0]
            codeb = item.split(',')[1]
            ffcode(codeb, codea, 'no', choice)

def scode6():   # https://www.cnblogs.com/bjwu/p/9038910.html
    with open('test.txt') as f:
        r = f.read().split('\n')
        r.remove('')  # 删除列表中的空行
    strset = r[0]
    print(strset)
    remove_digits = str.maketrans('', '', string.digits)   # 删除字符串中的数字
    res_letter = strset.translate(remove_digits)
    print(res_letter)


    remove_letter = str.maketrans('', '', string.ascii_letters)  # 删除字符串中的字母
    remove_letter = str.maketrans('', '', string.ascii_uppercase)  # 删除字符串中的大写字母
    num_letter = strset.translate(remove_letter)
    print(num_letter)


if __name__ == '__main__':
    scode6()

