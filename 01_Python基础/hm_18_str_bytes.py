
# 字节转化为字符串用下面的两种都可以
import sys
print('目前系统的编码为：', sys.getdefaultencoding())

print(str(b'example', encoding='utf-8'))    # example
print(bytes.decode(b'example'))

# 字符串转化为字节,用下面两种方法都可以
print(bytes('example', encoding='utf-8'))     # b'example'
print(str.encode('example'))                  # b'example'

