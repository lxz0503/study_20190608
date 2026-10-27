
###
###配套视频已出版，学习有疑问联系作者qq:2574674466###
###
#coding=utf-8
dict_1 = {'Name': 'Jack','Age':18,'Score':100}
print("操作字典元素之前，遍历并打印字典元素如下：")
for (key,value) in dict_1.items():
    print(key + ":" + str(value))

dict_1.clear()
print("操作字典元素之后，遍历并打印字典元素如下：")
print(dict_1)
for (key,value) in dict_1.items():
    print(key + ":" + str(value))
