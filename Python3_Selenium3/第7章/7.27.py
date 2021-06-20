#coding=utf-8
dict_1 = {'Name': 'Jack','Age':18,'Score':100}
print("操作字典元素之前，遍历并打印字典元素如下：")
for (key,value) in dict_1.items():
    print(key + ":" + str(value))

#删除字典元素 'Name': 'Jack'
del dict_1['Name']
print("删除一个元素后，遍历并打印字典元素如下：")
for (key,value) in dict_1.items():
    print(key + ":" + str(value))
