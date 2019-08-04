import socket
BUFSIZE = 1024
ip_port = ('127.0.0.1', 8080)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
res = s.connect_ex(ip_port)

while True:
    msg = input('>>: ').strip()    # 输入字符串
    if len(msg) == 0:
        continue
    if msg == 'quit':
        break
    s.send(msg.encode('utf-8'))    # 电脑只能发送字节，所以要用encode来编码
    act_res = s.recv(BUFSIZE)        # 电脑接受到字节
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