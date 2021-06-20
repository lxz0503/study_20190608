#coding=utf-8
dict_1 = {'Name': 'Jack','Age':18,'Score':100}
print("操作字典元素之前，遍历并打印字典元素如下：")
for (key,value) in dict_1.items():
    print(key + ":" + str(value))

del dict_1
print("操作字典元素之后，遍历并打印字典元素如下：")
print(dict_1)
for (key,value) in dict_1.items():
    print(key + ":" + str(value))
