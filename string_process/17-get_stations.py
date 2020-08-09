#!/usr/bin/env python3
# coding=utf-8

import re


def write_stations(stations, file_name):
    with open(file_name, 'w', encoding='utf_8_sig') as f:
        f.write(stations)

def read_stations(file_name):
    with open(file_name, 'r', encoding='utf_8_sig') as f:
        data = f.readline()
    return data


if __name__ == '__main__':
    test = """天津|TJP|重庆|CQW|aaa.com"""
    stations = re.findall(r'([\u4e00-\u9fa5]+)\|([A-Z]+)', test)
    print(stations)  # [('天津', 'TJP'), ('重庆', 'CQW')]
    stations = dict(stations)
    print(stations)  # {'天津': 'TJP', '重庆': 'CQW'}
    stations = str(stations)   # {'天津': 'TJP', '重庆': 'CQW'}
    print(stations)
    write_stations(stations, 'stations.txt')
    #
    stations = read_stations('stations.txt')
    print(type(stations))   # this is str
    stations = eval(read_stations('stations.txt'))   # use eval to change to dict
    print(type(stations), stations)   # this is dict
    from_stations = list(stations.keys())
    print(from_stations)     # ['天津', '重庆']
    from_stations = list(stations.values())
    print(from_stations)     # ['TJP', 'CQW']