import socket
import threading

BUFSIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 买手机, 只负责接收客户端请求，不负责发送和接收数据
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # 重用ip和端口
s.bind(('127.0.0.1', 8000))     # 手机插卡
s.listen(5)          # 手机待机

while True:                       # 新增接收链接循环,可以不停的接电话，即可对应多个client
    print("server端开始接受客户端连接")
    new_client, ip_port = s.accept()          # 手机接电话，accept之后，用conn来接收和发送数据
    print('接到来自%s的电话' % ip_port[0])
    while True:                     # 新增通信循环,可以不断的通信,收发消息
        try:      # 在windows上，如果client突然终止，服务端就会出现异常，
                  # 就需要加异常处理，但是在linux机器上不需要加异常处理
            msg = new_client.recv(BUFSIZE)      # 听消息,听话,recv是从内核态内存中取字节
            if len(msg) == 0:     # 这条break是MAC系统的解决方式,就不需要异常处理
                break             # 如果不加,那么正在链接的客户端突然断开,recv便不再阻塞,死循环发生
            # print(msg, type(msg))   # b'dir' <class 'bytes'>, 只能收发字节
            # conn.send(msg.upper())    # 发消息,说话
            new_client.send(b'HTTP/1.1 200 OK\r\n\r\n')  # 表示约定了http 协议
            new_client.send(b'<h1>hello</h1>')
        except Exception:
            break         # 异常处理结束,下面的conn.close()不会被执行
    # conn.close()                   # 挂电话
s.close()                          # 手机关机