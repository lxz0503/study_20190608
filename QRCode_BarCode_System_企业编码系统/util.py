#!/usr/bin/env python3
# coding=utf-8
import os


def mk_dir(file_path):   # create dir
    if not os.path.exists(file_path):
        os.mkdir(file_path)


def openfile(filename):    # open file and read content
    with open(filename) as f:
        r = f.read()
    return r


def inputbox(showstr, showorder, length):
    instr = input(showstr)
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


if __name__ == '__main__':
    r = inputbox('请输入验证码数量：', 1, 0)
    print(r)

