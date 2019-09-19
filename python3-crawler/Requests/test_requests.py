import requests


result = requests.get('https://wwww.baidu.com')
print(result.status_code, result.reason)    # 200 OK
# print(result.text)    # this can get the web content
print(result.headers)    # this can get request headers, it is a dictionary
print(result.request)     # this is a get request
print(result.url)      #
print(result.content)     # this can get the original web content
print(result.cookies)
print(result.history)

# request methods

requests.post('http://httpbin.org/post')
requests.put('http://httpbin.org/put')
requests.delete('http://httpbin.org/delete')
requests.head('http://httpbin.org/get')
requests.options('http://httpbin.org/get')

#
result = requests.get('http://httpbin.org/get')
print('start')
print(result.text)
print('end')

# request with parameters
result = requests.get('http://httpbin.org/get?name=xiaozhan&age=30')
print(result.text)
# request with parameters
data = {
        'name': 'xiaozhan',
        'age': 30
        }
result = requests.get('http://httpbin.org/get', params=data)
print(result.text)

# json
result = requests.get('http://httpbin.org/get')
print('json start')
print(result.json())
print('json end')

# download image and save it, image is binary code
result = requests.get('http://pic25.nipic.com/20121112/9252150_150552938000_2.jpg')
with open('test_image.jpg', 'wb') as f:
    f.write(result.content)

# add headers to get information from website,otherwise it will fail
headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
          }
result = requests.get('https://www.zhihu.com/explore', headers=headers)
print(result.text)

# request with post method
form_data = {
        'user': 'xiaozhan',
        'password': 30
        }
headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
          }
result = requests.post('http://httpbin.org/post', data=form_data, headers=headers)
print('post start')
print(result.text)    # print(result.text)
print('post end')

# response
result = requests.get('https://wwww.baidu.com')
# print(result.status_code, result.reason)    # 200 OK
# exit() if result.status_code != 200 else print('request successfully')
exit() if result.status_code != 200 else print('request successfully')

# upload files or image
files = {'file': open('test_image.jpg', 'rb')}
headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
          }
result = requests.post('http://httpbin.org/post', headers=headers, files=files)
print(result.text)

# get cookies
result = requests.get('https://wwww.baidu.com')
print(result.cookies)
for key,value in result.cookies.items():
    print(key + '=====' + value)

#
requests.get('http://httpbin.org/cookies/set/number/12345')
result = requests.get('http://httpbin.org/cookies')
print(result.text)




