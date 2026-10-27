#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/26/2022 10:47 AM
@file:set_option.py
@project:xiaozhan_git
"""
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os

f_dir = os.path.dirname(__file__) + '/data.csv'
df = pd.read_csv(f_dir,na_values='数据分析')
df.style.format(na_rep='数据缺失')
df.style.highlight_null()
print(df.head())
#
df = pd.DataFrame([[np.nan, 1.0, 'A'], [2.0, np.nan, 3.0]])
df.style.format(na_rep='MISS', precision=3)

