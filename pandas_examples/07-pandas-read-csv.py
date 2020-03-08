import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
import os

f_dir = os.path.dirname(__file__) + '/bug_record.csv'
df = pd.read_csv(f_dir, nrows=3)
# print(df)
f_dir_copy = os.path.dirname(__file__) + '/bug_record_copy.csv'
df.to_csv(f_dir_copy, index=False, header=False)    # ????????index?header
print('df is', df)

dates = pd.date_range('2/1/2018', periods=7)
# ts = pd.Series(np.arange(7), index=dates)
ts = pd.Series(dates)
print('ts is', ts)

# process csv
lines = list(csv.reader(open(f_dir)))
header, values = lines[0], lines[1:]
print('value is:', values)
data_dict = {h: v for h, v in zip(header, values)}
print(type(data_dict))
print(data_dict)
