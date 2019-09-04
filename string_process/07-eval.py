# eval()函数 练习
# eval(source[, globals[, locals]])
# 作用：
# 将字符串str当成有效的表达式来求值并返回计算结果。
# 参数：source：一个Python表达式或函数compile()返回的代码对象；
# globals：可选。必须是dictionary；
# locals：可选。任意map对象。

# 字符串转换成列表
a = "[[1,2], [3,4], [5,6], [7,8], [9,0]]"
print("a的类型是", type(a))    # <type 'str'>
b = eval(a)
print("b现在是一个列表", b)   # [[1, 2], [3, 4], [5, 6], [7, 8], [9, 0]]
print("b的类型是", type(b))    # list

# 字符串转换成字典
a = "{'city': 'beijing', 'population': 10000}"   # 双引号里面可以包含单引号，里面的字典格式不能用双引号
b = eval(a)
print(b)                     # {'city': 'beijing', 'population': 10000}
print("b现在是一个字典类型", type(b))     # <class 'dict'>

#  字符串转换成元组
a = "([1,2], [3,4], [5,6], [7,8], (9,0))"
b = eval(a)
print(b)           # ([1, 2], [3, 4], [5, 6], [7, 8], (9, 0))
print("b的类型是", type(b))       # <type 'tuple'>

# 直接进行数学运算
x = 1
y = 1
num1 = eval("x+y")
print(num1)

#  如果字符串是数字，将它转为数字类型，用eval
test_str = '-1234588888.8888888899999999999999999999999999'
out = eval(test_str)
print(type(out))      # <class 'int'>
print(out)