#!/usr/bin/env python3
# coding=utf-8
import logging.config
import logging

logging.config.fileConfig('Logger.conf')
logger = logging.getLogger('root')

logger.debug('this is debug')
logger.info('this is info')
logger.warning('this is warn')
logger.error('this is error')
logger.critical('this is critical')