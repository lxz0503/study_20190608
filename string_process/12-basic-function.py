# center()将字符串居中，空余部分用*补全
str_test = "[www.runoob.com]"
print("str_test.center(40, '*') : ", str_test.center(40, '*'))

# count() 方法用于统计字符串里某个字符出现的次数。可选参数为在字符串搜索的开始与结束位置
str_test = "www.runoob.com"
sub = 'o'
print("str_test.count('o'):", str_test.count(sub))    # str_test.count('o'): 3

sub = 'run'
print("str_test.count('run', 0, 10) : ", str_test.count(sub, 0, 10))    # str_test.count('run', 0, 10) :  1

# decode() 方法以指定的编码格式解码
str_test = "菜鸟教程"
str_utf8 = str_test.encode("UTF-8")   # UTF-8 编码： b'\xe8\x8f\x9c\xe9\xb8\x9f\xe6\x95\x99\xe7\xa8\x8b'
str_gbk = str_test.encode("GBK")     # GBK 编码： b'\xb2\xcb\xc4\xf1\xbd\xcc\xb3\xcc'
print(str_test)

print("UTF-8 编码：", str_utf8)
print("GBK 编码：", str_gbk)
print("UTF-8 解码：", str_utf8.decode('UTF-8', 'strict'))
print("GBK 解码：", str_gbk.decode('GBK', 'strict'))

# find()方法查找字串，返回字串的起始位置，否则返回-1. index()用法也类似,只不过没找到会返回异常
str1 = "Runoob example....wow!!!"
str2 = "exam"

print(str1.find(str2))
print(str1.find(str2, 5))   # 从下标5开始查找，默认到结尾
print(str1.find(str2, 10))

# join() 方法用于将序列中的元素以指定的字符连接生成一个新的字符串
s1 = "-"
s2 = ""
seq = ("r", "u", "n", "o", "o", "b")     # 字符串序列
seq_list = ["r", "u", "n", "o", "o", "b"]
print(s1.join(seq))     # r-u-n-o-o-b
print(s2.join(seq))     # runoob
print(s1.join(seq_list))

# ljust() 方法返回一个原字符串左对齐,并使用空格填充至指定长度的新字符串
# lstrip() 方法用于截掉字符串左边的空格或指定字符
# 从左到右移除字符串的指定字符，无字符集参数或为 None 时移除空格，
# str 时移除所有属于字符集子串的字符,一旦不属于则停止移除并返回字符串副本
str_test = 'www.example.com'
new_str = str_test.lstrip('cmowz.')   # 没看懂
print(new_str)            # example.com

# replace() 方法把字符串中的 old（旧字符串） 替换成 new(新字符串)，如果指定第三个参数max，则替换不超过 max 次
str_test = "this is string example....wow!!!"
replace_str = str_test.replace("is", "was", 3)
print(replace_str)

# rfind() 返回字符串最后一次出现的位置，如果没有匹配项则返回-1,和find()类似，只不过从右边开始查找
# rindex()也类似，从右边开始查找
# split() 通过指定分隔符对字符串进行切片，返回一个列表，如果第二个参数 num 有指定值，则分割为 num+1 个子字符串
str_test = "this is string example....wow!!!"
print(str_test.split())       # 以空格为分隔符
print(str_test.split('i', 1))   # 以 i 为分隔符
print(str_test.split('w'))     # 以 w 为分隔符

