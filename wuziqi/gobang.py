#!/usr/bin/env python3
# coding=utf-8

print('\033[1;37;41m-------简易五子棋---------\033[0m')  # 设置某一行显示不同的颜色
# 初始化棋盘
checkerboard = []
for i in range(10):
    checkerboard.append([])
    for j in range(10):
        checkerboard[i].append('-')


# 输出最后胜利的棋盘
def msg(flag_num):
    print('\033[1;30;46m--------------------------')
    print('   1  2  3  4  5  6  7  8  9  10')   # 输出行标号,3个空格，两个空格
    for i in range(len(checkerboard)):
        print(chr(i + ord('A')) + ' ', end=' ')   # 输出列标号,先打印每一行开头是A B C等
        for j in range(len(checkerboard[i])):
            print(checkerboard[i][j] + ' ', end=' ')   # 加end表示指定结束符，不换行
        print()   # 输出换行符
    print('-----------------------------\033[0m')
    #
    if flag_num == 1:
        print('\033[32m   持*棋子胜利******\033[0m')
    else:
        print('\033[32m   持o棋子胜利ooooooo\033[0m')


# how to play
def go():
    """简易五子棋"""
    finish = False
    flag_num = 1  # 当前下棋者标记
    flag_ch = '*'  # 当前下棋者棋子
    x = 0
    y = 0
    while not finish:
        # 每一下一个棋子就打印棋盘,设置某一区域显示不同的颜色
        print('\033[1;30;46m 输出当前棋盘--------------------------')
        print('   1  2  3  4  5  6  7  8  9  10')   # 输出行标号,3个空格，两个空格
        for i in range(len(checkerboard)):
            print(chr(i + ord('A')) + ' ', end=' ')   # 输出列标号
            for j in range(len(checkerboard[i])):
                print(checkerboard[i][j] + ' ', end=' ')   # 加end表示指定结束符，不换行
            print()   # 输出换行符
        print('-----------------------------\033[0m')
        # 判断当前下棋者
        if flag_num == 1:
            flag_ch = '*'
            print('\033[1;45m 请*输入棋子坐标（例如A1）:\033[0m', end=' ')  # 粉底黑字
        else:
            flag_ch = 'o'
            print('\033[1;33m 请o输入棋子坐标（例如J2）:\033[0m', end=' ')  # 黑底绿字

        # record chess position  棋子坐标
        position = input()
        ch = position[0]
        x = ord(ch) - 65
        y = int(position[1]) - 1
        # 判断坐标是否在棋盘范围内
        if x < 0 or x > 9 or y < 0 or y > 9:
            print('\033[31m****您输入的坐标有误，重新输入!\033[0m')
            continue
        # 判断坐标上是否有棋子
        if checkerboard[x][y] == '-':
            if flag_num == 1:
                checkerboard[x][y] = '*'
            else:
                checkerboard[x][y] = 'o'
        else:
            print('\033[31m*******您输入的位置已经有其他棋子，请重新输入！\033[0m')
            continue
        # 五子棋算法
        # 棋子坐标形式为'大写字母+1到10的数字'，例如A1，A为横坐标，1为纵坐标，将首字母转换为X坐标，用ord()函数获取字母对应的ASCII
        # 然后减去字母A的ASCII值,第二个数字转换为Y坐标，只需要减去1即可，因为索引从0开始
        # 判断棋子左侧
        if y - 4 >= 0:
            if checkerboard[x][y - 1] == flag_ch and checkerboard[x][y - 2] == flag_ch \
                    and checkerboard[x][y - 3] == flag_ch and checkerboard[x][y - 4] == flag_ch:
                print('left')
                finish = True
                msg(flag_num)
                break
        # 判断棋子右侧
        if y + 4 <= 9:
            if checkerboard[x][y + 1] == flag_ch and checkerboard[x][y + 2] == flag_ch \
                    and checkerboard[x][y + 3] == flag_ch and checkerboard[x][y + 4] == flag_ch:
                finish = True
                msg(flag_num)
                break
        # 判断棋子上方
        if x - 4 >= 0:
            if checkerboard[x - 1][y] == flag_ch and checkerboard[x - 2][y] == flag_ch \
                    and checkerboard[x - 3][y] == flag_ch and checkerboard[x - 4][y] == flag_ch:
                finish = True
                msg(flag_num)
                break
        # 判断棋子右上方
        if x - 4 >= 0 and y + 4 <= 9:
            if checkerboard[x - 1][y + 1] == flag_ch and checkerboard[x - 2][y + 2] == flag_ch \
                    and checkerboard[x - 3][y + 3] == flag_ch and checkerboard[x - 4][y + 4] == flag_ch:
                finish = True
                msg(flag_num)
                break
        # 判断棋子左上方
        if x - 4 >= 0 and y - 4 >= 0:
            if checkerboard[x - 1][y - 1] == flag_ch and checkerboard[x - 2][y - 2] == flag_ch \
                    and checkerboard[x - 3][y - 3] == flag_ch and checkerboard[x - 4][y - 4] == flag_ch:
                finish = True
                msg(flag_num)
                break
        flag_num *= -1      # 更换下棋者标记


if __name__ == '__main__':
    go()




