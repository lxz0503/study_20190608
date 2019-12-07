import requests
import json
def get_translate_date(word=None):
    url='http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
    Form_data = {'i':word, 'from':'AUTO','to': 'AUTO','smartresult': 'dict', 'client':'fanyideskweb',
                    'salt':'1512399450582','sign':'78181ebbdcb38de9b4a3f4cd1d38816b','doctype':'json',
                    'version': '2.1','keyfrom':'fanyi.web','action':'FY_BY_CLICKBUTTION','typoResult':'false'}
    response = requests.post(url, data=Form_data)                # 请求表单数据
    content = json.loads(response.text)                  # 将JSON格式字符串转字典
    print(content['translateResult'][0][0]['tgt'])             # 打印翻译后的数据
if __name__ == '__main__':
    get_translate_date('我爱数据')
