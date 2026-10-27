def multiple_table():
    """ 打印九九乘法表"""
    # 选中下方所有代码，按tab键，统一缩进
    row = 1
    while row <= 9:
        col = 1
        while col <= row:
            # 格式化输出，用-2d表示靠左对齐
            print("%d*%d=%d" % (row, col, row * col), end="\t")
            col += 1
        print("")  # 输出一个换行
        row += 1


if __name__ == "__main__":
    multiple_table()