import urllib
import urllib.request

with urllib.request.urlopen('http://www.baidu.com') as f:
    data = f.read()
    print('Status:', f.status, f.reason)
    # print('Data:', data.decode('utf-8'))

# send a post request
import urllib.parse

data = bytes(urllib.parse.urlencode({'word': 'hello'}), encoding='utf-8')
response = urllib.request.urlopen('http://httpbin.org/post', data=data)
print(response.read())

#
import socket
import urllib.error

try:
    response = urllib.request.urlopen('http://httpbin.org/get', timeout=0.1)
except urllib.error.URLError as e:
    if isinstance(e.reason, socket.timeout):
        print('TIME OUT')
# response
response = urllib.request.urlopen('https://httpbin.org')
print(response.read().decode('utf-8'))
print(response.status)
print(response.getheaders())      # a list
print(response.getheader('Server'))

# Request
request = urllib.request.Request('https://httpbin.org')
response = urllib.request.urlopen(request)
print(response.read().decode('utf-8'))


