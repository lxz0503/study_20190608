import pandas as pd
import numpy as np


cities_prices = {'beijing': 60000, 'shanghai': 59000, 'shenzhen': 58000}
apts = pd.Series(cities_prices)
# print("old values: %s" % apts['shanghai'])
# print("old values:", apts['shanghai'])
print(apts)
# print(type(apts))
# print(apts['beijing'])
# print(apts[['beijing', 'shanghai']])
# print(apts[apts < 60000])
# apts[apts < 60000] = 40000
# print(apts/2)
# print(np.square(apts))

data = {'city': ['beijing', 'shanghai', 'shenzhen', 'guangzhou'],
        'year': [2016, 2017, 2018, 2019],
        'house_price': [50000, 48000, 35000, 30000]}
data_frame = pd.DataFrame(data, columns=['year', 'city', 'house_price'])
print(data_frame)
