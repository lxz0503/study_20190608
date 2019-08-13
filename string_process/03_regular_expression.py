# study below website for re module
# https://www.runoob.com/python3/python3-reg-expressions.html
# re.match 尝试从字符串的起始位置匹配一个模式，如果不是起始位置匹配成功的话，match()就返回none
# .* 表示任意匹配除换行符（\n、\r）之外的任何单个或多个字符
# re.search 扫描整个字符串并返回第一个成功的匹配
# \w	匹配包括下划线的任何单词字符
# [^abc] 匹配除了a,b,c之外的字符
# [amk] 匹配 'a'，'m'或'k'
import re

p = re.compile(r'\d+')
result = p.split('one1two2three33four4')
# del result[-1]
result.pop()  # ['one', 'two', 'three', 'four']
print(result)

# find number
p = re.compile(r'\d+')
result = p.findall('one1two2three33four4')
print(result)   # ['1', '2', '33', '4']

# 注意到group()永远是原始字符串，group(1)、group(2)……表示第1、2、……个子串
p = re.compile(r'(\w+) (\w+)')
s = 'I say, hello han xiaoyang'
result = p.match(s)
print(result.group())    # I say
print(result.group(1))    # I
print(result.group(2).title())   # Say

# re.match
line = "Cats are smarter than dogs"
# .* 表示任意匹配除换行符（\n、\r）之外的任何单个或多个字符
matchObj = re.match(r'(.*) are (.*?) .*', line, re.M | re.I)
if matchObj:
    print("matchObj.group() : ", matchObj.group())     # Cats are smarter than dogs
    print("matchObj.group(1) : ", matchObj.group(1))   # Cats
    print("matchObj.group(2) : ", matchObj.group(2))   # smarter
else:
    print("No match!!")

# re.search

line = "Cats are smarter than dogs"
searchObj = re.search(r'(.*) are (.*?) .*', line, re.M | re.I)
if searchObj:
    print("searchObj.group() : ", searchObj.group())      # Cats are smarter than dogs
    print("searchObj.group(1) : ", searchObj.group(1))    # Cats
    print("searchObj.group(2) : ", searchObj.group(2))     # smarter
else:
    print("Nothing found!!")

#  match 是从字符串的起始处开始匹配,而search是搜索整个字符串中模式首次出现的位置

m = re.search('foo', 'seafood')
if m is not None:
    print(m.group())    # foo

m = re.match('foo', 'seafood')
if m is not None:
    print(m.group())    # nothing
# sub
p = re.compile(r'\w+')
s = 'xy 15 rt 3e,gep'
result = p.sub('10', s, 2)  # 10是被替换的内容，s是原来的字符串，2表示只替换匹配的前两个
print(result)   # 10 10 rt 3e,gep
# sub
phone = "2004-959-559 # 这是一个电话号码"
# 删除注释
num = re.sub(r'#.*$', "", phone)
print("电话号码 : ", num)      # 电话号码 :  2004-959-559
# 移除非数字的内容
num = re.sub(r'\D', "", phone)    # 电话号码 :  2004959559
print("电话号码 : ", num)

# findall
# 在字符串中找到正则表达式所匹配的所有子串，并返回一个列表，如果没有找到匹配的，则返回空列表。
# 注意： match 和 search 是匹配一次, findall 匹配所有
pattern = re.compile(r'\d+')  # 查找数字，+ 表示贪婪匹配
result1 = pattern.findall('runoob 123 google 456')
result2 = pattern.findall('run88oob123google456', 0, 10)

print(result1)     # ['123', '456']
print(result2)     # ['88', '12']

r = re.findall(r"alex?", "alexxx")  # 非贪婪匹配，因为加了？
print(r)    # ['alex']

# r = re.findall(r"alex+", "alexxx")  # .*或者.+ 或者+都是贪婪匹配
r = re.findall(r"alex.*", "alexxx")  # .*或者.+ 或者+都是贪婪匹配
# r = re.findall(r"alex.+", "alexxx")  # .*或者.+ 或者+都是贪婪匹配
print(r)                    # ['alexxx']

# 在字符串中找到正则表达式所匹配的所有子串，并把它们作为一个迭代器返回
it = re.finditer(r"\d+", "12a32bc43jf3")
for match in it:
    print(match.group())

#例如用 \w{4}匹配 RegExr was created   结果是RegE crea

line = "RegExr was created"
m = re.findall(r'\w{4}', line)
# if m is not None:
#     print(m.group())
print(m)    # ['RegE', 'crea']