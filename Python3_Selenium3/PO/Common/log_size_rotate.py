#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 4/28/2021 1:05 PM
# @Email = lxz_20081025@163.com
# @Name = log_size_rotate.py
import logging, time
from Common.function import projectPath
from logging import handlers


class FrameLog(object):
    kv = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, level='info', max_bytes=10 * 10, back_count=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):  # pathname是脚本全路径名字
        self.log_path = projectPath() + '/Logs/'
        self.log_name = self.log_path + time.strftime('%Y_%m_%d_') + 'log.log'
        self.logger = logging.getLogger(self.log_name)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.kv.get(level))  # 设置日志级别
        console = logging.StreamHandler()  # 设置往屏幕或者串口上输出
        console.setFormatter(format_str)  # 设置屏幕上显示的日志格式
        # 往文件里写入 # 指定文件大小自动生成文件的处理器
        th = handlers.RotatingFileHandler(filename=self.log_name, maxBytes=max_bytes, backupCount=back_count,
                                          encoding='utf-8')
        # 实例化TimedRotatingFileHandler
        # backupCount是备份文件个数，如果超过，则自动删除之前的日志,maxBytes是每个文件的大小
        th.setFormatter(format_str)  # 设置文件里log写入的格式
        self.logger.addHandler(console)  # 把对象添加到logger里
        self.logger.addHandler(th)

    def log(self):
        return self.logger


if __name__ == '__main__':
    lo = FrameLog()
    log = lo.log()
    log.error('error')
    log.debug('debug')
    log.info('info')
    log.critical('critical')
