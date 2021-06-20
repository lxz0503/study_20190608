#coding=utf-8
list_1 = [3,6,9,"selenium","8.9093",["a","B","C","abc"]]
print("以下为直接打印整个list列表：")
print(list_1)
print("\n") #换行操作
print("以下为逐个遍历列表的元素，并打印：")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)



#coding=utf-8
list_1 = [3,6,9,"selenium","8.9093",["a","B","C","abc"]]
print("append添加列表元素之前，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)
list_1.append("a_append")
print("\n") #换行操作
print("append添加列表元素之后，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)


#coding=utf-8
list_1 = [3,6,9,"selenium","8.9093",["a","B","C","abc"]]
print("append添加列表元素之前，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)
list_1.extend(['e','f','g'])
print("\n") #换行操作
print("append添加列表元素之后，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)

##### 5.10
#coding=utf-8
list_1 = [3,6,9,"selenium","8.9093",["a","B","C","abc"]]
print("append添加列表元素之前，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)
list_1.insert(0,"0") #指在列表的第1（0+1）个位置上添加元素"0"
print("\n") #换行操作
print("append添加列表元素之后，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)

####5.11
#coding=utf-8
list_1 = [3,6,9,"selenium","8.9093",["a","B","C","abc"]]
print("执行删除列表元素之前，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)
list_1.remove(3) #删除 '3'这个列表元素
print("\n") #换行操作
print("执行删除列表元素之后，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)



#5.12
list_1 = [3,6,9,"selenium","8.9093",["a","B","C","abc"]]
print("执行删除列表元素之前，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)
del list_1[1] #删除 位置序号为1的元素，也就是列表中第2个元素。
print("\n") #换行操作
print("执行删除列表元素之后，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)

#5.13
list_1 = [3,6,9,"selenium","8.9093","-9"]
print("执行删除列表元素之前，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)
pop_res = list_1.pop()
print("\n")
print("pop()方法返回的元素："+pop_res)
print("\n") #换行操作
print("执行删除列表元素之后，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)


#5.14
list_1 = [3,6,9,"selenium","8.9093","-9"]
print("列表分片之前，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)

print("\n") #换行操作
temp = list_1[3] #返回的是一个字符串，是列表中的第4个元素。
print(temp)

temp = list_1[2:4] #连续分片，返回的是一个新的列表temp,列表元素为老列表的第3，4个元素组成。
print(temp)
print("列表分片之后，遍历列表元素，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)

#5.15
list_1 = [3,6,9,"selenium","8.9093","-9"]
list_2 = [1,4,7,"python","9.9999","-10"]
print("遍历列表1，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)

print("遍历列表2，并打印")
for l in list_2: #for循环遍历所有的列表元素，并打印
    print(l)

list_3 = list_1 + list_2
print("遍历拼接后的列表，并打印")
for l in list_3:
    print(l)


#5.16
list_1 = [3,6,9,"selenium","8.9093","-9"]
print("遍历列表1，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)

list_3 = list_1*3
print("遍历拼接后的列表，并打印")
for l in list_3:
    print(l)


#5.17
list_1 = [1,2,3,4,5]
list_2 = [6,7,8,9,10]
print("遍历列表1，并打印")
for l in list_1: #for循环遍历所有的列表元素，并打印
    print(l)

print("遍历列表2，并打印")
for l in list_2: #for循环遍历所有的列表元素，并打印
    print(l)

print(list_1 > list_2)
print(list_1 < list_2)




