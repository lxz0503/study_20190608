# 定义一个函数sum_numbers
# 能够接受一个num的整数参数
# 计算1 +2 +3 ....+ num 的结果


def sum_numbers(num):
    # 1.函数出口，防止死循环
    if num == 1:
        return 1
    # 2.数字的累加 num + (1.....num - 1)
    tmp = sum_numbers(num - 1)
    return num + tmp


result = sum_numbers(10)
