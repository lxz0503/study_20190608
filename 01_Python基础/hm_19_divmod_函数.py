# python内置函数divmod()
# 本函数是实现a除以b，然后返回商与余数的元组。
# 如果两个参数a,b都是整数，那么会采用整数除法，结果相当于（a//b, a % b)。
# 如果a或b是浮点数，相当于（math.floor(a/b), a%b)

print('divmod(2, 4):', divmod(2, 4)[0])
print('divmod(28, 4):', divmod(28, 4))
print('divmod(27, 4):', divmod(27, 4))
print('divmod(25.6, 4):', divmod(25.6, 4))
print('divmod(2, 0.3):', divmod(2, 0.3))

# divmod(2, 4): (0, 2)
# divmod(28, 4): (7, 0)
# divmod(27, 4): (6, 3)
# divmod(25.6, 4): (6.0, 1.6000000000000014)
# divmod(2, 0.3): (6.0, 0.20000000000000007)
# abs()函数为取绝对值的函数
print(abs(-5.11))