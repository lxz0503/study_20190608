#!/usr/bin/env python3
# coding=utf-8
import yagmail
import os
import jinja2


def my_render(tpl_path, **kwargs):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(**kwargs)


def test_html():
    links = [{'title': 'beijing', 'href': 'http://aaa.com/1/2/3.shtml'},
             {'title': 'shanghia', 'href': 'http://aaa.com/1/2/4.shtml'},
             {'title': 'shenzhen', 'href': 'http://aaa.com/1/2/5.shtml'}]
    # result = my_render('hzfc.html', items=links)
    result = my_render('hzfc.html', **locals())
    # print(result)
    return result


if __name__ == '__main__':
    with open(r'send_email\performance.html') as f:
        test = f.read()          # read html content
    r = test_html()     # read dynamic html content
    yag = yagmail.SMTP(user="534188479@qq.com", password='ocndjpiwqtcdbhfg', host='smtp.qq.com')
    contents = ['this is a test',   # send string
                test,
                r,                  # send html content
                yagmail.inline('iterator.png'),    # built-in picture
                'base.cfg']         # attachment
    yag.send(to='lxz_20081025@163.com', subject='SendHelloTest', contents=contents)