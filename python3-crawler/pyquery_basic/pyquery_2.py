# coding=utf-8
from pyquery import PyQuery as pq

html = '''
    <div href="wrap">
        hello nihao
        <ul class="s_from">
            asdasd
            <link class='active1 a123' href="http://asda.com"><a>asdadasdad12312</a></link>
            <link class='active2' href="http://asda1.com">asdadasdad12312</link>
            <link class='movie1' href="http://asda2.com">asdadasdad12312</link>
        </ul>
    </div>
'''
# attr 为获取/修改属性    css 添加style属性
# attr()方法返回的是第一个节点的属性值。
# 那要取多个li节点的属性值，要怎么做呢？这就要结合items()方法来实现。items()方法是返回的节点的生成器generator object PyQuery.items：
# attr()方法只有一个参数时，是获取节点的属性值，有两个参数时，是给节点添加属性及属性值，第一个参数时属性，第二个参数时属性值
# html()和text()如果没参数，则是获取属性的文本值，如果有参数，则是改变或者添加节点的属性值
# print(doc('.div_tag #ul_tag li'))
# 上述代码是通过.div_tag获取class为div_tag的节点，然后通过#ul_tag获取id为ul_tag的节点，最后返回所有的li节点
# print(doc('.div_tag #ul_tag').find("li"))
# find("li")是把所有li节点及子节点都查找出来
doc = pq(html)
its = doc("link").items()
for it in its:
    print("修改:%s" % it.attr('class', 'active'))
    print("添加:%s" % it.css('font-size', '14px'))
# 修改:<link class="active" href="http://asda.com"><a>asdadasdad12312</a></link>
# 添加:<link class="active" href="http://asda.com" style="font-size: 14px"><a>asdadasdad12312</a></link>
# 修改:<link class="active" href="http://asda1.com">asdadasdad12312</link>
# 添加:<link class="active" href="http://asda1.com" style="font-size: 14px">asdadasdad12312</link>
# 修改:<link class="active" href="http://asda2.com">asdadasdad12312</link>
# 添加:<link class="active" href="http://asda2.com" style="font-size: 14px">asdadasdad12312</link>

