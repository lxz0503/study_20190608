row = 1
while row <= 9:
    col = 1
    while col <= row:
        # 格式化输出，用-2d表示靠左对齐
        print("%d*%d=%d" % (row, col, row * col), end="\t")
        col += 1
    print("")
    row += 1