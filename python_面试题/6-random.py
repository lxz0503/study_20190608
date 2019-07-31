# 如何生成一个随机数
import random

print(random.random())             # 用于生成一个0到1的随机符点数: 0 <= n < 1.0
print(random.randint(1, 1000))     # 用于生成一个指定范围内的整数

# 三元表达式与列表解析
# 三元就是三个运算符
# 变量 = 值-if条件-else 值二
l = []
for i in range(10):
    l.append("egg%s" % i)
print(l)

l = ["egg%s" % i for i in range(10)]
print("无判断条件生成列表", l)
# 三元表达式,生成列表
# 主体是for循环，二元是"egg%s" % i, 3元是判断
# 其实就是把几行的内容精简一下，写到一行
l = ["egg%s" % i for i in range(10) if i > 5]
print("采用三元表达式生成列表", l)      # ['egg6', 'egg7', 'egg8', 'egg9']