# Given a 32-bit signed integer, reverse digits of an integer.
#
# Example 1:
#
# Input: 123
# Output: 321
# Example 2:
#
# Input: -123
# Output: -321
# Example 3:
#
# Input: 120
# Output: 21
def int_reverse(x):
    if x >= 2**31-1 or x <= -2**31:
        return 0
    else:
        int_str = str(x)       # str函数把整型转化为字符串
        if x >= 0:
            revst = int_str[::-1]
        else:
            temp = int_str[1:]       # 通过切片取负号以后的数字
            temp2 = temp[::-1]       # 倒序输出
            revst = "-" + temp2      # 在字符串前面添加负号
        if int(revst) >= 2**31-1 or int(revst) <= -2**31:
            return 0
        else:
            return int(revst)        # int函数把字符串数字转化为整型
# function call
res = int_reverse(-1230)
print(res)                           # -321
# 先练习下面的int函数
res = int('-1230')
res = int('-0123')      # -123,int函数会自动去掉前面的0
print(res)
for x in range(11):
    print(x)