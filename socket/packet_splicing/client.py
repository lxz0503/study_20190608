import socket
import time

client=socket.socket()
client.connect(('127.0.0.1',7878))

client.send('123'.encode('utf-8'))
client.send('abc'.encode('utf-8'))
client.close()


# 两次发送信息时间间隔太短，数据小，造成服务端一次收取