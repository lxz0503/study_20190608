# 解压序列，应用场景：取一个很大的序列的开头和结尾
# a, b, c = [1, 2, "beijing"]
a, b, c = (1, 2, "beijing")    # 拆分元组
# a, b, c = {"beijing": "shoudu", "shanghai": 2000, "nanjing": 3000}
# print(a, b, c)  #

l = [1, 2, 3, 4, 5, 6]
a, *d, c = l    # *d 也可以用*_来替代,表示不需要这部分
print(a, *d, c)     # 1 2 3 4 5 6
print(d)            # [2, 3, 4, 5]   print(_)

# 拆分列表 元组
seq = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
for a, b, c in seq:
    print('a={0}, b={1}, c={2}'.format(a, b, c))

# 定义元组,用逗号分隔开的字符 就是元组
a = 1, 2, 3
print(type(a))      # <class 'tuple'>