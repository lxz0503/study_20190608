# 打印log到屏幕，同时也保存到文件里
# !/usr/bin/env python3
# coding=utf-8

import logging
from logging import handlers

class Logger(object):
    kv = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, file_name, level='info', when='D', back_count=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):   # pathname是脚本全路径名字
        self.logger = logging.getLogger(file_name)
        format_str = logging.Formatter(fmt)         # 设置日志格式
        self.logger.setLevel(self.kv.get(level))    # 设置日志级别
        console = logging.StreamHandler()                 # 设置往屏幕或者串口上输出
        console.setFormatter(format_str)                 # 设置屏幕上显示的日志格式
        # 往文件里写入 # 指定时间间隔自动生成文件的处理器
        th = handlers.TimedRotatingFileHandler(filename=file_name, when=when, backupCount=back_count, encoding='utf-8')
        # 实例化TimedRotatingFileHandler
        # backupCount是备份文件个数，如果超过，则自动删除之前的日志,when是间隔的时间单位
        th.setFormatter(format_str)         # 设置文件里log写入的格式
        self.logger.addHandler(console)          # 把对象添加到logger里
        self.logger.addHandler(th)


if __name__ == '__main__':
    log = Logger('logging.log', level='debug').logger    # 初始化一个Logger实例，以后直接用这个实例来处理log
    test = 'xiaozhan'
    log.info(f'print test name is {test}')   # this is similar to print, but more powerful
    log.info('start to test')
    try:
        result = 10 / 0
    except Exception as e:
        log.error('Failed to get result')

