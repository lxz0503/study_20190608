# 如何实现 “1, 2, 3” 变成[‘1’, ’2’, ’3’] ?
#
# 如何实现[‘1’, ’2’, ’3’]变成[1, 2, 3] ?
# 比较： a = [1, 2, 3]
# 和
# b = [(1), (2), (3)]
# 以及
# b = [(1,), (2,), (3,)]
# 的区别？

s = "1, 2, 3"
print(type(s))
new_s = s.split(',')
print(new_s)            # ['1', ' 2', ' 3']

new_s = "1,2,3".split(',')
print("just one line to a str list", new_s)      # ['1', '2', '3']

n_s = []
for i in new_s:
    n_s.append(int(i))
print(n_s)              # [1, 2, 3]

n_s = [int(x) for x in ['1','2','3']]
print("just one line code", n_s)

b = [(1,), (2,), (3,)]
for i in b:
    # print(type(i))
    print(i)      # (1,) (2,) (3,)

# 如果列表里既有数字又有字符串，只能通过for循环来操作，转换成字符串
# 如果只有字符串，就直接用"".join(列表名字)转换成字符串
s = ""
l = [1, 23, "sss"]
for i in l:
    s += str(i)
print(s)

