#! /usr/bin/ env python3
# encoding=utf-8
import json

path = 'test.txt'
records = [json.loads(line) for line in open(path)]    # get all data and store in a list, each element is a dict
print(records)
print(records[0]['tz'])
# tz is a key in the dict, rec is a dict
time_zones = [rec['tz'] for rec in records if 'tz' in rec]
print(time_zones[:10])

from collections import defaultdict
def get_counts2(sequence):
    counts = defaultdict(int)
    for x in sequence:
        counts[x] += 1    #  统计次数，字典的key不能重复，所以自动过滤掉重复的key
    return counts

res = get_counts2(time_zones)
print(res)

from collections import Counter
counts = Counter(time_zones)
res_5 = counts.most_common(5)
print(res_5)

import pandas as pd
import numpy as np
from pandas import DataFrame, Series

frame = DataFrame(records)
print(frame.columns)   # print all column names
print(frame['tz'].value_counts())    # 统计某一列中元素出现的次数

clean_tz = frame['tz'].fillna('Missing')  # use Missing to replace NA
clean_tz[clean_tz == ''] = 'Unknown'
tz_counts = clean_tz.value_counts()
print(tz_counts)

results = Series([x.split()[0] for x in frame.a.dropna()])
print(results[:5])

cframe = frame[frame.a.notnull()]
print('cframe:', cframe)

operating_system = np.where(cframe['a'].str.contains('Windows'), 'Windows', 'Not Windows')
print(operating_system[:5])

by_tz_os = cframe.groupby(['tz', operating_system])
agg_counts = by_tz_os.size().unstack().fillna(0)
print('agg_counts is\n', agg_counts[:5])

indexer = agg_counts.sum(1).argsort()
print(indexer[:5])



