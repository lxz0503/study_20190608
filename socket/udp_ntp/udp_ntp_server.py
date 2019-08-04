from socket import *
import subprocess
import time

ip_port = ('127.0.0.1', 9003)
bufsize = 1024

udp_server = socket(AF_INET, SOCK_DGRAM)
udp_server.bind(ip_port)

while True:
    # 收消息
    cmd, addr = udp_server.recvfrom(bufsize)
    print('用户命令----->', cmd)     # 接收到的是二进制形式的码流

    server_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 发消息
    udp_server.sendto(server_time.encode('utf-8'), addr)
udp_server.close()