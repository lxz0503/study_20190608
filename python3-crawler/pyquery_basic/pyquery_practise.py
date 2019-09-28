# coding=utf-8
from pyquery import PyQuery as pq

# 三种基本用法,也就是三种初始化方法
#   #是查找id的标签  .是查找class 的标签  link是查找link标签 中间的空格表示里层
# doc =pq(html)          #解析html字符串
# doc =pq("http://news.baidu.com/")   #解析网页
# doc =pq("./a.html")     #解析html文本

html = '''
    <div id="wrap">
        <ul class="s_from">
            asdasd
            <link href="http://asda.com">asdadasdad12312</link>
            <link href="http://asda1.com">asdadasdad12312</link>
            <link href="http://asda2.com">asdadasdad12312</link>
        </ul>
    </div>
'''
# URL
doc = pq("http://news.baidu.com/")
print(doc('head'))    # 把head标签里面的内容全部打印

# 文本
doc = pq(filename='test_example.html')
print(doc('body'))

# 字符串
doc = pq(html)
# print(doc("#wrap .s_from link"))     # s_from不一定是wrap的子对象，没必要紧挨着，只是一个大致的定位，最终目的是查找最里层的link标签
# print(doc('link'))
# print(doc('#wrap'))
print('find element')
items = doc("#wrap")
print(items)
print("类型为:%s" % type(items))
link = items.find('.s_from')
print(link)
link = items.children()
print('it is %s' % link)         # find方法和children 方法都可以获取里层标签
# parent可以查找出外层标签包括的内容，与之类似的还有parents,可以获取所有外层节点
print('find parent tag')
items = doc(".s_from")
parent_href = items.parent()
print(parent_href)

# 基本的CSS选择器
print('CSS selector start')
# 查找元素
print('CSS selector end')
# find
html = '''
    <div href="wrap">
        hello nihao
        <ul class="s_from">
            asdasd
            <link class='active1 a123' href="http://asda.com">asdadasdad12312</link>
            <link class='active2' href="http://asda1.com">asdadasdad12312</link>
            <link class='movie1' href="http://asda2.com">asdadasdad12312</link>
        </ul>
    </div>
'''
doc = pq(html)
items = doc("link.active1.a123")         # 查找link标签，再继续查找class里面含有active1和a123的link
# items = doc(".s_from .active1.a123")         # 有空格，表示选择里层的，没有空格，表示是并列条件
# 先找到class  s_from
print(items)
# 查找兄弟元素
siblings_href = items.siblings()     # siblings 返回了同级的其他标签
print('the siblings are:', siblings_href)

# 






