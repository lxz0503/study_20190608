#coding:utf-8
import requests
import jsonpath
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}
response = requests.get('https://www.lagou.com/lbs/getAllCitySearchLabels.json', headers=headers)

dict_data = json.loads(response.content)   # 转为字典

print(jsonpath.jsonpath(dict_data,'$..name'))
