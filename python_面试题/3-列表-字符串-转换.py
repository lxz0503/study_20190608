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

