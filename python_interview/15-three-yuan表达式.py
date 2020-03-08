# 三元表达式与列表解析
# 三元就是三个运算符
# 变量 = 值1 if条件  else 值2
a = 1
result = 'xiaoming' if a == 1 else 'sam'
print(result)             # xiaoming

############
l = []
for i in range(10):
    l.append("egg%s" % i)
print(l)

l = ["egg%s" % i for i in range(10)]
print(l)
# 三元表达式,生成列表
# 主体是for循环，二元是"egg%s" % i,3元是判断
# 其实就是把几行的内容精简一下，写到一行
l = ["egg%s" % i for i in range(10) if i > 5]
# l = ("egg%s" % i for i in range(10) if i > 5)
print(l)