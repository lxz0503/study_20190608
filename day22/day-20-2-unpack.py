# 解压序列，应用场景：取一个很大的序列的开头和结尾
# a, b, c = [1, 2, "beijing"]
a, b, c = (1, 2, "beijing")
# a, b, c = {"beijing": "shoudu", "shanghai": 2000, "nanjing": 3000}
# print(a, b, c)  #

l = [1, 2, 3, 4, 5, 6]
a, *d, c = l    # *d 也可以用*_来替代
print(a, *d, c)     # 1 2 3 4 5 6
print(d)            # [2, 3, 4, 5]   print(_)

