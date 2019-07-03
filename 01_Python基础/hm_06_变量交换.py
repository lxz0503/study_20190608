a = 10
b = 20
# 解法1.使用临时变量,理解为a,b,c三个杯子倒水
# c = a   # 把a杯子里的水倒入c,此时a杯子空了
# a = b   # 把b杯子里的水倒入a，此时b杯子空了
# b = c   # 把c杯子里的水（来源于第一步）倒入b，此时c杯子空了
# print(a)
# print(b)

# 解法2.使用几次加法和减法
# a = a + b
# b = a - b
# a = a - b
# print(a)
# print(b)

# 解法3.python专用方法，使用元组给变量赋值即可实现简单的数字交换
# a, b = (b, a)
a, b = b, a
print(a)
print(b)
