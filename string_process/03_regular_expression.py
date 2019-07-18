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

# 注意到group(0)永远是原始字符串，group(1)、group(2)……表示第1、2、……个子串
p = re.compile(r'(\w+) (\w+)')
s = 'I say, hello han xiaoyang'
result = p.match(s)
print(result.group(0))    # I say
print(result.group(1))    # I
print(result.group(2).title())   # Say

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

# findall
# 在字符串中找到正则表达式所匹配的所有子串，并返回一个列表，如果没有找到匹配的，则返回空列表。
# 注意： match 和 search 是匹配一次, findall 匹配所有
pattern = re.compile(r'\d+')  # 查找数字
result1 = pattern.findall('runoob 123 google 456')
result2 = pattern.findall('run88oob123google456', 0, 10)

print(result1)     # ['123', '456']
print(result2)     # ['88', '12']