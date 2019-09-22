import requests

# upload files or image
print('start to upload image')
files = {'file': open('test_image.jpg', 'rb')}
headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
          }
result = requests.post('http://httpbin.org/post', headers=headers, files=files)
print(result.text)
print('end to upload image')

# get cookies
result = requests.get('https://wwww.baidu.com')
print(result.cookies)
for key, value in result.cookies.items():
    print(key + '=====' + value)

# session, this can not get cookies because in the same browser
requests.get('http://httpbin.org/cookies/set/number/123456789')
result = requests.get('http://httpbin.org/cookies')
print(result.text)
# {
#   "cookies": {}
# }

# this can get correct cookies
s = requests.Session()
s.get('http://httpbin.org/cookies/set/number/123456789')
result = s.get('http://httpbin.org/cookies')
print(result.text)
# {
#   "cookies": {
#     "number": "123456789"
#   }
# }

# certificate
result = requests.get('https://www.12306.cn')
print(result.status_code)
# set proxy
proxies = {
    'http': 'http://127.0.0.1:9743',
    'https': 'https://127.0.0.1:9743',
}
# result = requests.get('https://www.12306.cn', proxies=proxies)

# authentication
# from requests.auth import HTTPBasicAuth

# result = requests.get('http:120.27.34.24:9001', auth=('user', '123'))

# exception
from requests.exceptions import ReadTimeout, HTTPError, RequestException
try:
    result = requests.get('http://www.123.com', timeout=1)
except ReadTimeout:
    print('timeout')
except HTTPError:
    print('http error')
finally:
    print(result.status_code)