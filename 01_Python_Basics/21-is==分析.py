# 首先要知道Python中对象包含的三个基本要素，分别是：id(身份标识)、type(数据类型)和value(值)
# 只有数值型和字符串型的情况下，a is b才为True，当a和b是tuple，list，dict或set型时，a is b为False
# 数值型和字符串是不可变对象

# ==是python标准操作符中的比较操作符，用来比较判断两个对象的value(值)是否相等
# is也被叫做同一性运算符，这个运算符比较判断的是对象间的唯一身份标识，也就是id是否相同

a = 1
b = 1
print(a is b)      # True
# print(id(a))       # 其实在比较两个数值的id
# print(id(b))

#---------
a = "beijing"
b = "beijing"
print(a is b)      # True

# ---------
a = [1, 2, 3]
b = [1, 2, 3]
print("list", a is b)      # False

a = set([1, 2, 3])
b = set([1, 2, 3])
print("集合", a == b)
print("集合", a is b)


a = (1, 2, 3)
b = (1, 2, 3)
print("元组", a == b)      # True
print("元组", a is b)      # False

a = {"beijing": 1000, "shanghai": 2000}
b = {"beijing": 1000, "shanghai": 2000}
print(a == b)      # True
print(a is b)      # False

