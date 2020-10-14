# study below website for re module
# https://www.runoob.com/python3/python3-reg-expressions.html
# re.match 尝试从字符串的起始位置匹配一个模式，如果不是起始位置匹配成功的话，match()就返回none
# .* 表示任意匹配除换行符（\n、\r）之外的任何单个或多个字符
# re.search 扫描整个字符串并返回第一个成功的匹配, 需要加group()来提取结果
# \w	匹配包括下划线的任何单词字符
# [^abc] 匹配除了a,b,c之外的字符
# [amk] 匹配 'a'，'m'或'k'
# 用?表示非贪婪匹配，原理是?遇到后面的匹配后马上停止，例如he.*?(\d+)
# 使用re.S参数以后，正则表达式会将这个字符串作为一个整体，在整体中进行匹配,可以忽略其中的换行符
# re?    匹配0个或1个由前面的正则表达式定义的片段，非贪婪方式
# \s	匹配任意空白字符，等价于 [\t\n\r\f]
# re*	匹配0个或多个的表达式。
# re+	匹配1个或多个的表达式
# \s*?  匹配0个多个空白字符，非贪婪，表示有时候有空白字符，有时候没有空白字符
# 匹配的时候尽量用非贪婪匹配,加上?
# .*?能匹配好多乱七八糟的东西，除了换行符,参考最下面的例子
# 再匹配网页Html的时候，要加上结束标签,尽量多利用<> 来匹配
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

#
name = 'NIGHTLYSPIN'
with open('reg_text', 'r') as fd:
    content = fd.read()
    found = re.search('%s=(.*?)\n' % name, content)  # 因为后面有换行符，所以是非贪婪匹配
    if found is not None:
        print(found.group())    # NIGHTLYSPIN=vx20200221095524_vx7-SR0640-native
        print(found.group(1).strip())  # vx20200221095524_vx7-SR0640-native   表示匹配第一个分组，即第一个小括号里面的内容
    else:
        print('nothing')

name = 'NIGHTLYSPIN'
content = 'NIGHTLYSPIN=vx20200221095524_vx7-SR0640-native  '
found = re.search('%s=(.*)' % name, content)   # 这里必须是贪婪匹配
if found:
    print(found.group())            # NIGHTLYSPIN=vx20200221095524_vx7-SR0640-nativ
    print(found.group(1).strip())   # vx20200221095524_vx7-SR0640-native

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

# 待匹配的文本：<img src="/UploadFiles/image/20140304/20140304094318_2971.png" alt="" />

p = re.compile(r'<img src="(.*?)"')
url = '<img src="/UploadFiles/image/20140304/20140304094318_2971.png" alt=" />'
# m = re.match(r'<img src="(.*?)"', url)
m = p.match(url)
if m is not None:
    print('the url is:', m.group(1))                # /UploadFiles/image/20140304/20140304094318_2971.png

# not greedy match
content = 'hello 1234567 demo'
result = re.match('^h.*?(\d+).*demo$', content)   # .* will try to match as less characters until meets \d
print(result.group(1))        # 1234567

# greedy match
content = 'hello 1234567 demo'
result = re.match('^h.*(\d+).*?demo$', content)
print(result.group(1))            # 7

# re.S
content = 'hello 1234567 demo \
           this is a world'
result = re.match('^h.*(\d+).*?world$', content)
print(result.group(1))       # 7

content = '''hello 1234567 demo
             this is a world'''
result = re.match('^h.*(\d+).*?world$', content, re.S)
print(result.group(1))       # 7

# practise
html = """ 
     <div id ="songs-list">
     <h2 class="title">经典老歌</h2>
     <li data-view="7">一路上有你</li>
     <li data-view="8">
     <a href="www.13.com" singer="任贤齐">沧海一声笑</a>
     </li>
     <li>
     <li data-view="9">
     <a href="www.1223.com" singer="齐秦">往事随风</a></li>
     </li>
     </div>
"""
result = re.search('<li.*?singer="(.*?)">(.*?)</a>', html, re.S)
if result:
    print(result.group(1), result.group(2))

# re.findall() will match all results and put them into a list
result = re.findall('<li.*?href="(.*?)".*?singer="(.*?)">(.*?)</a>', html, re.S)
print(result)    # [('www.13.com', '任贤齐', '沧海一声笑'), ('www.1223.com', '齐秦', '往事随风')]
for i in result:
    print(i)

#
result = re.findall('<li.*?>\s*?(<a.*?>)?(\w+)(</a>)?\s*?</li>', html, re.S)
print(result)    # [('www.13.com', '任贤齐', '沧海一声笑'), ('www.1223.com', '齐秦', '往事随风')]
for i in result:
    print(i[1])

# re.sub()
html = re.sub('<a.*?>|</a>', '',  html)
print(html)
#      <div id ="songs-list">
#      <h2 class="title">经典老歌</h2>
#      <li data-view="7">一路上有你</li>
#      <li data-view="8">
#      沧海一声笑
#      </li>
#      <li>
#      <li data-view="9">
#      往事随风</li>
#      </li>
#      </div>
result = re.findall('<li.*?>\s*?(\w+)\s*?</li>', html, re.S)
print(result)
for i in result:
    print(i)
# 一路上有你
# 沧海一声笑
# 往事随风

#
# with open('douban.html') as f:
#     # print(f.read())
#     r = f.read()
r = """          <li class="">
            <div class="cover">
              <a href="https://book.douban.com/subject/34779925/?icn=index-latestbook-subject" title="what ia real life">
                <img src="https://img3.doubanio.com/view/subject/m/public/s33465670.jpg" class=""
                  width="115px" height="172px" alt="waht is real life">
              </a>
            </div>
            <div class="info">
              <div class="title">
                <a class="" href="https://book.douban.com/subject/34779925/?icn=index-latestbook-subject"
                  title="what is real life">what is life</a>
              </div>
              <div class="author">
                France Alan
              </div>
              <div class="more-meta">
                <h4 class="title">
                  what is real life
                </h4>
                <p>
                  <span class="author">
                    李晓瞻
                  </span>
                  /
                  <span class="year">
                    2019-8
                  </span>
                  /
                  <span class="publisher">
                    china ren min daxue
                  </span>
                </p>
                <p class="abstract">

                </p>
              </div>
            </div>
          </li>
"""
pattern = re.compile('<li.*?cover.*?href="(.*?)".*?title="(.*?)".*?more-meta.*?author">(.*?)</span>.*?year">(.*?)</span>.*?publisher">(.*?)</span>.*?</li>', re.S)
result = re.findall(pattern, r)
# print(result)
for i in result:
    url, title, author, year, publisher = i
    print(url.strip(),title.strip(),author.strip(),year.strip(),publisher.strip())
    # print(title.strip())
    # print(author.strip())
    # print(year.strip())
    # print(publisher.strip())

# 正则表达式改变一个文件的内容
import os
with open('reg_text', 'r') as f:
    with open('reg_text.bak', 'w') as f1:
        for line in f:
            f1.write(re.sub('timestamp', 'lixiaozhan', line))
os.remove('reg_text')
os.rename('reg_text.bak', 'reg_text')

#

a = './vxworks-7/pkgs_v2/net/ipnet/coreip-2.1.1.1/src/iptcp/src/iptcp.c'
b = a.split('iptcp')[0] + 'iptcp/config/iptcp_config.h'
print(b)
# ./vxworks-7/pkgs_v2/net/ipnet/coreip-2.1.1.1/src/iptcp/config/iptcp_config.h

# 用正则来切分字符串
s = 'info:xiaozhang 33 shandong'
res = re.split(r":| ", s)
print(res)   # ['info', 'xiaozhang', '33', 'shandong']

# 正则匹配不是以4和7结尾的手机号
tels = ['13412345674','18912341231','1310086','18812347777']
for tel in tels:
    # ret = re.match(r'1\d{9}[0-3,5-6,8-9]',tel)
    ret = re.match(r'1\d{9}[^47]', tel)
    if ret:
        print('the expected result is', ret.group())
    else:
        print('%s is not the result' % tel)


