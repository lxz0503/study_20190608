# coding=utf-8

from pyquery import PyQuery as pq

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
its = doc("link").items()      # 有很多link标签，所以要想抓取多个link标签，必须用items()，返回的是一个迭代器
# print(type(its))   # <class 'generator'>
for it in its:
    print(it)

# 获取属性信息
doc = pq(html)
its = doc("link").items()       # pyquery多个节点的遍历用items()方法
for it in its:
    print(it.attr('href'))
    # print(it.attr('class'))
    print(it.attr.href)

# 获取文本信息
doc = pq(html)
its = doc("link").items()
for it in its:
    print(it.text())     # asdadasdad12312

# 获取文本信息
print('获取html')
doc = pq(html)
its = doc("link").items()
for it in its:
    print(it.html())         # asdadasdad12312

# 添加移除class标签，已经存在的不会添加
doc = pq(html)
its = doc("link").items()
for it in its:
    print("添加:%s" % it.addClass('active1'))
    print("移除:%s" % it.removeClass('active1'))
# 添加:<link class="active1 a123" href="http://asda.com">asdadasdad12312</link>
#
# 移除:<link class="a123" href="http://asda.com">asdadasdad12312</link>
#
# 添加:<link class="active2 active1" href="http://asda1.com">asdadasdad12312</link>
#
# 移除:<link class="active2" href="http://asda1.com">asdadasdad12312</link>
#
# 添加:<link class="movie1 active1" href="http://asda2.com">asdadasdad12312</link>
#
# 移除:<link class="movie1" href="http://asda2.com">asdadasdad12312</link>





