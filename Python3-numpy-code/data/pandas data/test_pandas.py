#! /user/bin/env python3

import pandas as pd
import os

f_dir = os.path.dirname(__file__) + '/taobao_data.csv'
df = pd.read_csv(f_dir, delimiter=',', encoding='gb2312', header=0)

print(df)