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
# remove 移除标签
doc = pq(html)
its = doc("div")
print('移除前获取文本结果:\n%s' % its.text())
it = its.remove('ul')
print('移除后获取文本结果:\n%s' % it.text())
# 移除前获取文本结果:
# hello nihao
# asdasd
# asdadasdad12312
# asdadasdad12312
# asdadasdad12312
# 移除后获取文本结果:
# hello nihao