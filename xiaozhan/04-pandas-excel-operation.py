import pandas as pd

# read data from excel
result = pd.read_excel(r'F:\xiaozhan_git\study_20190608\xiaozhan\performance.xls', sheet_name='ARM')
print(result)


# write DataFrame into excel
data = {'city': ['beijing', 'shanghai', 'shenzhen', 'guangzhou'],
        'year': [2016, 2017, 2018, 2019],
        'house_price': [50000, 48000, 35000, 30000]
        }    # 每一列数据

data_frame = pd.DataFrame(data, columns=['year', 'city', 'house_price'])
data_frame1 = pd.DataFrame(data, columns=['year', 'city', 'house_price'])

with pd.ExcelWriter(r'F:\xiaozhan_git\study_20190608\xiaozhan\write_excel.xls') as writer:
    data_frame.to_excel(writer, sheet_name='Sheet1')
    data_frame1.to_excel(writer, sheet_name='Sheet2')
