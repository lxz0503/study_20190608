import socket
ip_port = ('127.0.0.1', 8081)    # 电话卡
BUFSIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 买手机
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # 重用ip和端口
s.bind(ip_port)     # 手机插卡
s.listen(5)          # 手机待机

while True:                       # 新增接收链接循环,可以不停的接电话
    conn, addr = s.accept()          # 手机接电话
    print('接到来自%s的电话' % addr[0])
    while True:                     # 新增通信循环,可以不断的通信,收发消息
        msg = conn.recv(BUFSIZE)      # 听消息,听话
        if len(msg) == 0:
            break             # 如果不加,那么正在链接的客户端突然断开,recv便不再阻塞,死循环发生
        print(msg, type(msg))   # b'dir' <class 'bytes'>, 只能收发字节
        conn.send(msg.upper())    # 发消息,说话
    conn.close()                   # 挂电话
s.close()                          # 手机关机