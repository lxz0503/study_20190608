#! /user/bin/env python3
# coding=utf-8
import pandas as pd
import os

f_dir = os.path.dirname(__file__) + '/taobao_data.csv'
df = pd.read_csv(f_dir, delimiter=',', encoding='utf-8', header=0)

print(df)