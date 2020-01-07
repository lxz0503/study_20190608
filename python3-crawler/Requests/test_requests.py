import requests
import json


result = requests.get('https://wwww.baidu.com')
# the result status is 200, result reason is OK
print('the result status is {}, result reason is {}'.format(result.status_code, result.reason))
# print(result.text)    # this can get the web content
print('the header is {}'.format(result.headers))    # this can get request headers, it is a dictionary
print('the request type is {}'.format(result.request))     # this is a get request
print('the url is {}'.format(result.url))      #
print('the original content of this website is {}'.format(result.content))     # this can get the original web content
print('the cookies is {}'.format(result.cookies))
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
print('the type of the returned text is {}'.format(type(result.text)))     # return is str
# print(result.content)    # return is bytes
print('end')

# request with parameters
result = requests.get('http://httpbin.org/get?name=xiaozhan&age=30')
print(result.text)

# request with parameters
data = {
        'name': 'xiaozhan',
        'age': 30
        }
result = requests.get('http://httpbin.org/get', params=data, headers='')
print(result.text)

# json
result = requests.get('http://httpbin.org/get')
print('json start')
print(result)   # <Response [200]>
print(result.json())   # <Response [200]>
print(type(result.json()))     # <class 'dict'>
# store the response into a json file. result.json() change the format from str to json
json.dump(result.json(), open('test.json', 'w'))
print('json end')

# anti-serialization

dict1 = json.load(open('test.json', 'r'))
print('the content of file test.json after anti-serilized is {},type is {}'.format(dict1, type(dict1)))
# download image and save it, image is binary code

result = requests.get('http://pic25.nipic.com/20121112/9252150_150552938000_2.jpg')
with open('test_image.jpg', 'wb') as f:   # it must be wb mode, binary mode
    f.write(result.content)

# add headers to get information from website.otherwise it will fail
headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
          }
result = requests.get('https://www.zhihu.com/explore', headers=headers)
print(result.content)

# request with post method
form_data = {                       # it is a dictionary type
        'user': 'xiaozhan',
        'password': 30
        }
headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
          }
result = requests.post('http://httpbin.org/post', data=form_data, headers=headers)
print('post start')
# print(result.text)    # print(result.text)
print(type(json.dumps(result.json(), indent=True)))     # str
print('post end')

# response
result = requests.get('https://wwww.baidu.com')
# print(result.status_code, result.reason)    # 200 OK
# exit() if result.status_code != 200 else print('request successfully')
exit() if result.status_code != 200 else print('request successfully')







