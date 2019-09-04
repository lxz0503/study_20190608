# string change to bytes
a = '123'
str_to_bytes = a.encode()
print(str_to_bytes)       # b'123'

# bytes change to string

a = b'hello world'
print(type(a))       #  <class 'bytes'>
bytes_to_str = a.decode('utf-8')
print(type(bytes_to_str))       # <class 'str'>
print(bytes_to_str)         # hello world