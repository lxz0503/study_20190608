print("{0[0]}.{0[1]}".format(('baidu','com')))
# baidu.com

print("{0:.2f} {1:.1f}".format(3.1415926, 4.23))
# 3.14

# 基本语法是通过 {} 和 : 来代替以前的 %

msg = ['wang', 10]
print('my name is {0}, {0} age is {1}'.format(*msg))

msg = {'name': 'wang', 'age': 10}
print('my name is {name}, {name} age is {age}'.format(**msg))
# my name is wang, wang age is 10

# 左对齐
print('{:*<10}'.format('分割线'))
print('{:*^10}'.format('分割线'))   # 居中
# 右对齐

print('{:*>10}'.format('分割线'))
a = '{:*>10}'.format('分割线')
print(a)

# 分割线*******
# ***分割线****
# *******分割线