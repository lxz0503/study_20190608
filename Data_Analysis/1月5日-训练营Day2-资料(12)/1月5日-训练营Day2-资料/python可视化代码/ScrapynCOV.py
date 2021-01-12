import requests
import json
# 国内疫情数据

china_url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
"referer": "https://news.qq.com/zt2020/page/feiyan.htm? from=timeline&isappinstalled=0"
}
response = requests.get(china_url,headers=headers).json()
data = json.loads(response['data'])
# 保存数据
with open('./国内疫情7.json','w',encoding="utf-8") as f:
    f.write(json.dumps(data,ensure_ascii=False,indent=2))