#coding=utf=8
#首先给一个变量赋值
a = 10
if a > 10:
    print("数字大于10")
elif a < 10:
    print("数字小于10")
else:
    print("数字等于10")




#coding=utf-8
list1 = ["selenium","appium","python","automation"]

#使用for循环来遍历列表list1中的所有的元素
#第一种方式
for l in list1:
    print(l)

#第二种方式

for index in range(len(list1)):
    print(list1[index])



#coding=utf-8
for i in range(10):
    print(i)
print("***************")
for j in range(2,10,2):
    print(j)
print("***************")
print(type(range(10)))


