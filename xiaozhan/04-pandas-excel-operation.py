import pandas as pd
import os

# read data from excel
f_dir = os.path.dirname(__file__) + '/performance.xls'
result = pd.read_excel(f_dir, sheet_name='ARM')
print(result)


# write DataFrame into excel
data = {
        'city': ['beijing', 'shanghai', 'shenzhen', 'guangzhou'],
        'year': [2016, 2017, 2018, 2019],
        'house_price': [50000, 48000, 35000, 30000]
        }    # 每一列数据

data_frame = pd.DataFrame(data, columns=['year', 'city', 'house_price'])
data_frame1 = pd.DataFrame(data, columns=['year', 'city', 'house_price'])

w_dir = os.path.dirname(__file__) + '/write_excel.xls'
with pd.ExcelWriter(w_dir) as writer:
    data_frame.to_excel(writer, sheet_name='Sheet1')
    data_frame1.to_excel(writer, sheet_name='Sheet2')
