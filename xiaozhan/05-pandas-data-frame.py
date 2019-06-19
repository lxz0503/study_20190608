import pandas as pd
import numpy as np

data = {'city': ['beijing', 'shanghai', 'shenzhen', 'guangzhou'],
        'year': [2016, 2017, 2018, 2019],
        'house_price': [50000, 48000, 35000, 30000]
        }    # 每一列数据
data_frame = pd.DataFrame(data, columns=['year', 'city', 'house_price'])
print(data_frame)
print(data_frame.values)
print(data_frame.values[0])
print(data_frame.values[0][2])

# another example
frame = pd.DataFrame(np.arange(9).reshape(3, -1),  # -1 means generating columns automatically
                     index=['a', 'b', 'c'],   # 每行的名字
                     columns=['beijing', 'shanghai', 'hangzhou'] # 每列的名字
                     )
print(frame)
print(frame.ix['a':'b'])  # get value from index a to index b
# print(frame[frame.beijing>0]) # get value from column beijing that are greater than 0