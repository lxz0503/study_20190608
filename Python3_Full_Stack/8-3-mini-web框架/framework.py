#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/15/2022 5:27 PM
@file:framework.py
@project:openpyxl_excel
"""
import time,os
import pymysql
import json
from jinja2 import FileSystemLoader, Environment
from log_time_rotate import FrameLog

lo = FrameLog()
log = lo.log()


def get_sql_data(sql):    # 查询数据库，获取想要的数据
    conn = pymysql.Connect(db="test_result", user="root", password="123win", charset="utf8")
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()  # 数据存在元组里面
    cursor.close()
    conn.close()
    return result

def jinja_render(template_dir, html_file):      # 渲染HTML页面
    sql = "select * from ia_result"    # 这个命令会根据需求变化，
    result = get_sql_data(sql)   # 从数据库获取数据，格式是小元组组成的大元组，每个小元组就是一行数据
    # print(result)
    # 获取数据完毕,用Jinja2来渲染html模板
    template = Environment(loader=FileSystemLoader(template_dir)).get_template(html_file)  # 模板文件所在目录名字
    # 用**locals()可以取到所有局部变量，相当于直接传递给了index.html文件，来替换里面的对应变量。
    # 所以要注意变量的命名，必须和html模板里面的变量相同
    response_body = template.render(**locals())  # 下面一行效果一样
    # response_body = template.render(result=result)    # result变量存在于index.html模板中
    return response_body

# 渲染HTML页面，这里只是做测试，所以返回了json字符串,用到了元组转字典列表
def jinja_render_dict(template_dir, html_file):
    sql = "select * from ia_result"    # 这个命令会根据需求变化，
    sql_result = get_sql_data(sql)   # 从数据库获取数据，格式是元组
    print('sql result:', sql_result)
    # 把元组转成字典列表（每个元素都是一个字典），用到了字典生成式
    result = [{
        'name': row[0],
        'status': row[1],
        'arch': row[2],
        'sprint': row[3]
    } for row in sql_result]
    print('result:', result)
    # start 把列表转化成json字符串格式,这部分代码不是应用于这里的，只是顺道加上作为备用
    json_str = json.dumps(result, ensure_ascii=False)  # 如果要显示中文，就添加 ensure_ascii=False
    # end
    # 获取数据完毕,用Jinja2来渲染html模板
    # template = Environment(loader=FileSystemLoader(template_dir)).get_template(html_file)  # 模板文件所在目录名字
    # 用**locals()可以取到所有局部变量，相当于直接传递给了index.html文件，来替换里面的对应变量。
    # 所以要注意变量的命名，必须和html模板里面的变量相同
    # response_body = template.render(**locals())  # 下面一行效果一样
    # response_body = template.render(result=result)    # result变量存在于index.html模板中
    return json_str


def index():  # 处理index.html
    status = '200 OK'
    response_header = [('Server', 'niginx')]
    # 获取数据完毕,用Jinja2来渲染html模板
    # response_body = jinja_render('template', 'index.html')
    response_body = jinja_render('template', 'index.html')
    return status, response_header, response_body  # 返回一个元组


def center():  # 处理center.html,
    status = '200 OK'
    response_header = [('Server', 'niginx'),
                       ('Content-type', 'text/html;charset=utf-8')]
    # 获取数据完毕,用Jinja2来渲染html模板
    # response_body = jinja_render('template', 'index.html')
    response_body = jinja_render_dict('template', 'center.html')
    return status, response_header, response_body  # 返回一个元组


def not_found():
    status = '404 Not Found'
    response_header = [('Server', 'niginx')]
    # web处理后的数据
    data = time.ctime()
    # 返回一个元组
    return status, response_header, data

# 定义带有参数的装饰器,下面的函数返回一个装饰器
# def route(path):
#     def decorator(func):          # 当执行装饰器的时候就需要把路由添加到路由列表
#         # 当装饰函数的时候只添加一次路由即可
#         route_list.append((path, func))
#         def inner():
#             result = func()
#             return result
#         return inner
#     # 返回一个装饰器
#     return decorator

# 路由列表，内容是URL和对应处理函数组成的元组
route_list = [
    ('/index.html', index),
    ('/center.html', center)
]

def handle_request(req_path):
    # 如果处理的页面较少，可以写多个分支语句，如果很多，就用路由列表的方式
    log.info('req_path is %s', req_path, exc_info=1)
    # 遍历路由列表
    for path, func in route_list:  # 元组拆包
        if req_path == path:
            # 找到了指定路由，执行对应的处理函数  exc_info=1表示异常写入日志，无则NoneType: None
            log.info('找到了对应的路由和处理函数:%s', req_path, exc_info=1)
            result = func()
            return result
    else:     # 如果for循环没有找到这个路径，则走到这个else语句
        log.error('for循环没有找到对应的路由:%s', req_path, exc_info=1)
        result = not_found()
        return result

# def handle_request(req_path):
#     # 如果处理的页面较少，可以写多个分支语句，如果很多，就用路由的方式
#     print('req_path is', req_path)
#     if req_path == '/index.html':
#         result = index()
#         return result
#     elif req_path == '/center.html':
#         result = center()
#         return result
#     else:
#         result = not_found()
#         return result

if __name__ == '__main__':
    handle_request('/index.html')
    jinja_render_dict('template', 'index.html')
    # jinja_render('template', 'index.html')
