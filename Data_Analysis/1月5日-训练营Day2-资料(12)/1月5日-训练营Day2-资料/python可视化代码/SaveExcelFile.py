import json
import pandas as pd

# 读取文件
with open('./国内疫情7.json','r',encoding='utf-8') as f:
    data = f.read()
# 将数据转成Python数据格式
data = json.loads(data)
lastUpdateTime = data['lastUpdateTime'] # 获取中国所有的数据
chinaAreaDict = data['areaTree'][0]
# 获取省级数据
provinceList = chinaAreaDict['children']
china_citylist = []
for x in range(len(provinceList)):
    province = provinceList[x]['name']
    province_list = provinceList[x]['children']
    for y in range(len(province_list)):
        city = province_list[y]['name']
        total = province_list[y]['total']
        today = province_list[y]['today']
        china_dict = {'province': province, 'city': city, 'total': total,
                      'today': today}
        china_citylist.append(china_dict)
# 创建全国total数据-dataframe
chinaTotaldata = pd.DataFrame(china_citylist)
confirmlist = []
suspectlist = []
deadlsit = []
heallist = []
deadRatelist = []
healRatelist = []
for value in chinaTotaldata['total'].values.tolist():
    confirmlist.append(value['confirm'])
    suspectlist.append(value['suspect'])
    deadlsit.append(value['dead'])
    heallist.append(value['heal'])
    deadRatelist.append(value['deadRate'])
    healRatelist.append(value['healRate'])
chinaTotaldata['confirm']  = confirmlist
chinaTotaldata['suspect']  = suspectlist
chinaTotaldata['dead']  = deadlsit
chinaTotaldata['heal']  = heallist
chinaTotaldata['deadRate']  = deadRatelist
chinaTotaldata['healRate']  = healRatelist
# 创建全国today数据-dataframe
today_confirmlist = []
today_confirmCutslist = []
for value in chinaTotaldata['today'].values.tolist():
    today_confirmlist.append(value['confirm'])
    today_confirmCutslist.append(value['confirmCuts'])
chinaTotaldata['today_confirm']  = today_confirmlist
chinaTotaldata['today_confirmCuts']  = today_confirmCutslist
# 删除total和today列 chinaTotaldata.drop(['total','today'],axis=1,inplace = True)
# 保存到Excel
from openpyxl import load_workbook
book = load_workbook('国内疫情.xlsx')
writer = pd.ExcelWriter('国内疫情.xlsx',engine='openpyxl')
writer.book = book
writer.sheets = dict((ws.title,ws) for ws in book.worksheets)
chinaTotaldata.to_excel(writer,sheet_name=lastUpdateTime[:lastUpdateTime.find(' ')],index=False)
writer.save()
writer.close()
