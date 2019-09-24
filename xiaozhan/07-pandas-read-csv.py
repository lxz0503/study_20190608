import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

# df = pd.read_csv(r'F:\xiaozhan_git\study_20190608\xiaozhan\bug_record.csv')
df = pd.read_csv(r'F:\xiaozhan_git\study_20190608\xiaozhan\bug_record.csv', nrows=3)
# print(df)
df.to_csv(r'F:\xiaozhan_git\study_20190608\xiaozhan\bug_record_copy.csv', index=False, header=False)
# df = pd.read_csv(r'F:\xiaozhan_git\study_20190608\xiaozhan\bug_record_copy.csv')
print(df)

dates = pd.date_range('2/1/2018',periods=7)
# ts = pd.Series(np.arange(7), index=dates)
ts = pd.Series(dates)
print(ts)

# process csv
lines = list(csv.reader(open(r'F:\xiaozhan_git\study_20190608\xiaozhan\bug_record.csv')))
header, values = lines[0], lines[1:]
print('value is:', values)
data_dict = {h: v for h, v in zip(header, values)}
print(type(data_dict))
print(data_dict)
