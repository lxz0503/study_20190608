#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:1/25/2024 11:18 AM
@file:log_record.py
"""
import logging
import time
from logging import handlers


class Logger(object):
    kv = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, file_name, level='debug', when='D', back_count=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):  # pathname is full path
        self.logger = logging.getLogger(file_name)
        format_str = logging.Formatter(fmt)  # log format
        self.logger.setLevel(self.kv.get(level))  # log level
        console = logging.StreamHandler()  # print to console
        console.setFormatter(format_str)  # log format on console
        # write to file
        th = handlers.TimedRotatingFileHandler(filename=file_name, when=when, backupCount=back_count, encoding='utf-8')
        # TimedRotatingFileHandler
        # backupCount
        th.setFormatter(format_str)  # log format
        self.logger.addHandler(console)  #
        self.logger.addHandler(th)


# curTime = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
# log_name = 'test_' + curTime + '.log'
log_name = 'test_log/test.log'
log = Logger(log_name, level='debug').logger
# log.info('start to test')

if __name__ == '__main__':
    cmd = 'start to test'
    log.debug('--- send=%s' % cmd)

