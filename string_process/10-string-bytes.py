#!/usr/bin/env python3
# coding=utf-8
# string change to bytes, it needs encode
a = '123'
str_to_bytes = a.encode()
print(str_to_bytes)       # b'123'

# bytes change to string, it needs to decode

# a = b'hello world'
a = b'uname -a\r\nLinux PEK-QCAO1-D2 3.2.0-23-generic #36-Ubuntu SMP Tue Apr 10 20:39:51 UTC 2012 x86_64 x86_64 x86_64 GNU/Linux\r\n'
print('a type is', type(a))       #  <class 'bytes'>
bytes_to_str = a.decode('utf-8')
print(type(bytes_to_str))       # <class 'str'>
print(bytes_to_str)         # hello world