import socket
import struct
import json

BUFSIZE = 2048   # 设置此处为128就会看到粘包现象
ip_port = ('127.0.0.1', 8080)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
res = s.connect_ex(ip_port)

while True:
    msg = input('>>: ').strip()    # 输入字符串
    if len(msg) == 0:
        continue
    if msg == 'quit':
        s.shutdown(2)
        s.close()
        break
    s.send(msg.encode('utf-8'))    # 电脑只能发送字节，所以要用encode来编码
    # 2.接收 struct 封装的头 字节形式 ,  接收4个字节 head
    head = s.recv(4)
    # 3.struct反解 ,获得自定义报头的长度
    dic_length = struct.unpack('i', head)[0]
    # 4.接收自定义字典报头内容 字节形式
    head_dic = s.recv(int(dic_length))
    # 5.反序列化成自定义字典,先解码再反序列化,反序列化就是从字符串变成字典
    dic = json.loads(head_dic.decode('utf-8'))
    # 6.得到 真实内容的长度
    content_length = dic['size']
    print("真实数据长度是", content_length)
    # 7.设置一个字节变量 用于接收真实数据
    content = b''
    # 8 设置一个客户端接收长度
    recv_size = 0
    # 9 当客户端接收长度 小于 源数据长度,一直接收
    while recv_size < content_length:
        # 累加 真实数据,以字节形式
        content += s.recv(2048)
        tmp_content_len = len(content)
        print("tmp content length is ", tmp_content_len)
        # 累加 客户端接收的长度
        recv_size += len(content)
        print("recv_size is", recv_size)
    # 接收完毕,解码内容
    print(content.decode('utf-8'), end='')
    # print(content)

    # print(act_res.decode('GBK'), end='')      # 根据具体环境修改解码方式,windows中文默认GBK,公司英文系统utf-8

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