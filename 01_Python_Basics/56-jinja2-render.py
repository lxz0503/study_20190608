#!/usr/bin/env python3
# coding=utf-8
import os
import jinja2

def my_render(tpl_path, **kwargs):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(**kwargs)


def test_simple():
    title = 'Title H '
    items = [{'href': 'a.com', 'caption': 'ACaption'},
             {'href': 'b.com', 'caption': 'BCaption'}]
    content = 'This is content'
    result = my_render('simple.html', **locals())  # **locals() can get all local variables in test_simple()
    print(result)


def test_html():
    links = [{'title': 'beijing', 'href': 'http://aaa.com/1/2/3.shtml'},
             {'title': 'shanghia', 'href': 'http://aaa.com/1/2/4.shtml'},
             {'title': 'shenzhen', 'href': 'http://aaa.com/1/2/5.shtml'}]
    # result = my_render('hzfc.html', items=links)
    result = my_render('hzfc.html', **locals())
    print(result)

if __name__ == '__main__':
    # test_simple()
    test_html()