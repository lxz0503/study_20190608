import os
import re

s = "./IKEMain.log:0xffff8000005b7850 (tLogin55dc70): The task been terminated because it triggered an exception that raised the signal 11"

c = s.count('th')

#查看函数定义，参数里面带=号的可以不要，但是没有=的必须要传入参数
print(c)
m = re.search("exception", s)
if m is not None:
    print(m.group())
    print(m.group().upper())
    print(m.group().lower())


config = ' -add '.join(['_WRS_CONFIG_COMPONENT_IPDHCPS=y',
                            '_WRS_CONFIG_COMPONENT_IPIKE=y',
                            '_WRS_CONFIG_COMPONENT_IPIPSEC=y',
                            '_WRS_CONFIG_COMPONENT_IPMCP=y',
                            '_WRS_CONFIG_COMPONENT_IPRIP=y',
                            '_WRS_CONFIG_COMPONENT_IPFIREWALL=y',
                            '_WRS_CONFIG_COMPONENT_FEATURE_IPNET_INET6=y'])
print(config)

if "IPIKE" in config:
    print("true")
# 下面的字符串格式化，{}是占位符，格式化就是将占位符里面的内容替换为其他内容
#test = "I am {name},age {a}"
#v = test.format(name="alex", a=19)

# 下面的等同于上面的实现
test = "I am {0},age {1}"
v = test.format("alex",19)
print(v)

#
test = "aaa222"
v = test.isalpha()
print(v)

test = {
    "netifs": [
        {
            "device": {
                "name": "gei",
                "unit": 0,
                "id": "gei0"
            },
            "inet": {
                "address": "30.1.1.5",
                "prefixlen": 24,
                "gateway": "30.1.1.1"
            }
        }
     ]
}
print(type(test))

# expandtabs()    set the size of the tab，以\t作为分隔符

test = "username\temail\tpassword\n" \
       "beijing\tbeijing@123c.om\t123\n" \
       "shanghai\tshanghai@234.com\t234\n" \
       "shenzhen\tshenzhen@456.com\t456"
v = test.expandtabs(20)
print(v)
#
test = "aLex"
v = test.swapcase()
v = test[0:-1]  # aLe
print(v)

v = range(10)
for item in v:
    print(item,end="#")
print()

#如果列表里既有数字又有字符串，只能通过for循环来操作，转换成字符串
#如果只有字符串，就直接用"".join(列表名字)转换成字符串
s = ""
l = [1,23,"sss"]
for i in l:
    s = s + str(i)
print(s)

# v = l.clear()
# print(l)

li = [1,2,3,"aa"]
l.extend(li)
print(l)      # [12, 23, 'sss', 1, 2, 3, 'aa']

a = [1,2,3]
b = [1,2,3]
# c = a + b
a.extend(b)    # this is equal with c = a + b
print(a)

v = l.index(2)
print(v)

l.pop()   # remove the last value
print(l)    # [12, 23, 'sss', 1, 2, 3]

l.remove(1)   # remove the first 1 if you have multiple 1
print(l)

# tuple can not be added, removed,modified.

# 字典
info = {
    "a": 100,
    "beijing": 200,
    2: "aaaa",
    True: 300,
}

for item in info.values():
    print(item)

for item in info:
    print(item)