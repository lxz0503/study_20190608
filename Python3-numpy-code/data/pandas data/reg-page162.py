#!/usr/bin/env python3
# coding=utf-8

import pandas as pd

df = pd.read_csv('getlinks.csv')
print(df.head())
print(df.link.str.extract('(\d+)'))
#
print(df.link.str.extract('(.*)/(\d+)'))
# column name  ?P<URL>, put your column name within the angle bracket
print(df.link.str.extract('(?P<URL>.*)/(?P<ID>\d+)'))