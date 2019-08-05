import socket
BUFSIZE = 1024    # 设置此处为128就会看到粘包现象
ip_port = ('127.0.0.1', 8080)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
res = s.connect_ex(ip_port)

while True:
    msg = input('>>: ').strip()    # 输入字符串
    if len(msg) == 0:
        continue
    if msg == 'quit':
        # break        # 会直接进行s.close操作，关闭tcp链接
        s.shutdown(2)
        s.close()
        break
    s.send(msg.encode('utf-8'))    # 电脑只能发送字节，所以要用encode来编码
    # act_res = s.recv(BUFSIZE)        # 电脑接受到字节,可以设置为每次取128字节，就会看到粘包现象
    act_res = s.recv(128)        # 电脑接受到字节,可以设置为每次取128字节，就会看到粘包现象
    print(act_res.decode('GBK'), end='')      # 根据具体环境修改解码方式

# >>: dir
#  驱动器 D 中的卷是 New Volume
#  卷的序列号是 02F9-2904
#
#  D:\xiaozhan_git\study_20190608\socket\tcp_remote_runcmd 的目录
#
# 2019/07/31  22:09    <DIR>          .
# 2019/07/31  22:09    <DIR>          ..
# 2019/07/31  21:54               423 tcp_client_remote.py
# 2019/07/31  22:09               892 tcp_server_remote.py
#                2 个文件          1,315 字节
#                2 个目录 305,300,795,392 可用字节

# 下面就是粘包现象，通过修改client端接收缓冲区大小为128字节，可以迅速复现
# D:\Python\python.exe D:/xiaozhan_git/study_20190608/socket/tcp_remote_runcmd/tcp_client_remote.py
# >>: dir
#  驱动器 D 中的卷是 New Volume
#  卷的序列号是 02F9-2904
#
#  D:\xiaozhan_git\study_20190608\socket\tcp_remote_runcmd 的目录
#
# 201>>: ipconfig
# 9/08/05  11:05    <DIR>          .
# 2019/08/05  11:05    <DIR>          ..
# 2019/08/05  11:05             1,125 tcp_client_remot>>:
# ipconfig
# >>: e.py
# 2019/08/05  10:50             1,445 tcp_server_remote.py
#                2 个文件          2,570 字节
#                2 个>>: ipconfig
# 目录 300,836,909,056 可用字节
#
# Windows IP 配置
#
#
# 无线局域网适配器 无线网络连接:
#
# >>: ipconfig
#
#    本地链接 IPv6 地址. . . . . . . . : fe80::dd89:a791:ed45:8157%15
#    IPv4 地址 . . . . . . . . . . . . : 192.168.3.25
#    子>>: