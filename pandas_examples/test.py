#!/usr/bin/env python3
# coding=utf-8
import pandas as pd
from pyecharts.charts import Bar
from pyecharts import options as opts
from datetime import datetime

df = pd.read_excel('release_data.xls', sheet_name='ARM')
print(df)