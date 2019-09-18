import requests


result = requests.get('https://wwww.baidu.com')
print(result.status_code, result.reason)    # 200 OK
# print(result.text)    # this can get the web content
print(result.headers)    # this can get request headers, it is a dictionary
print(result.request)     # this is a get request
print(result.url)      #
print(result.content)     # this can get the original web content
print(result.cookies)