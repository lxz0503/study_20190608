# this is udp,so you have to input several times for cmd
# after you input dir for several times, it can show the result
from socket import *
ip_port = ('127.0.0.1', 9003)
bufsize = 1024

udp_client = socket(AF_INET, SOCK_DGRAM)


while True:
    msg = input('>>: ').strip()     # COPY udp_server_remote.py D:\
    udp_client.sendto(msg.encode('utf-8'), ip_port)

    data, addr = udp_client.recvfrom(bufsize)
    print(data.decode('GBK'), end='')         # windows7 is GBK 或者utf-8

# 在家里电脑上的演示：
# >>: python3 D:\xiaozhan_git\study_20190608\01_Python基础\hm_01_hello.py
# hello
# 60
# the scale is 65.87%
# 10
# re.compile('\\w+\\d+')
# your are not our employee
# aaaa