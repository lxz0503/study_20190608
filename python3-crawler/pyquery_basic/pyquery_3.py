#　http://www.imooc.com/article/266913
# https://www.cnblogs.com/gj5379/p/8514535.html
# coding=utf-8
from pyquery import PyQuery as pq
html = '''
    <div href="wrap">
        hello nihao
        <ul class="s_from">
            asdasd
            <link class='active1 a123' href="http://asda.com"><a>helloasdadasdad12312</a></link>
            <link class='active2' href="http://asda1.com">asdadasdad12312</link>
            <link class='movie1' href="http://asda2.com">asdadasdad12312</link>
        </ul>
    </div>
'''
doc = pq(html)
its = doc("link:first-child")
print(its)                # link节点
print('第一个标签:%s' % its)
its = doc("link:last-child")
print('最后一个标签:%s' % its)
its = doc("link:nth-child(2)")
print('第二个标签:%s' % its)
its = doc("link:gt(0)")       #从零开始
print("获取0以后的标签:%s" % its)
its = doc("link:nth-child(2n-1)")
print("获取奇数标签:%s" % its)
its = doc("link:contains('hello')")
print("获取文本包含hello的标签:%s" % its)

# 第一个标签:<link class="active1 a123" href="http://asda.com"><a>helloasdadasdad12312</a></link>
# 最后一个标签:<link class="movie1" href="http://asda2.com">asdadasdad12312</link>
# 第二个标签:<link class="active2" href="http://asda1.com">asdadasdad12312</link>
# 获取0以后的标签:<link class="active2" href="http://asda1.com">asdadasdad12312</link>
#             <link class="movie1" href="http://asda2.com">asdadasdad12312</link>
# 获取奇数标签:<link class="active1 a123" href="http://asda.com"><a>helloasdadasdad12312</a></link>
#             <link class="movie1" href="http://asda2.com">asdadasdad12312</link>
# 获取文本包含hello的标签:<link class="active1 a123" href="http://asda.com"><a>helloasdadasdad12312</a></link>