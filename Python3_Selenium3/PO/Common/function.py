#!/usr/bin/env python3
# coding=utf-8
import configparser
import os

# 获取项目路径
def projectPath():
    print(os.path.realpath(__file__))
    print('a', os.path.split(os.path.realpath(__file__)))
    return os.path.split(os.path.realpath(__file__))[0].split('C')[0]


# 返回config.ini文件中testUrl
def configUrl():
    config = configparser.ConfigParser()
    config.read(projectPath() + "config.ini")
    return config.get('testUrl', 'url')


if __name__ == '__main__':
    print(projectPath())
