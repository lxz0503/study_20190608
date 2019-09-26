# 可以用这个来演示http server端,然后用浏览器来模拟client端，运行127.0.0.1:8000，浏览器里就会显示hello
import socket
ip_port = ('127.0.0.1', 8000)    # 电话卡
BUFSIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 买手机
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # 重用ip和端口
s.bind(ip_port)     # 手机插卡
s.listen(5)          # 手机待机

while True:                       # 新增接收链接循环,可以不停的接电话
    print("server端开始接受客户端连接")
    conn, addr = s.accept()          # 手机接电话
    print('接到来自%s的电话' % addr[0])

    while True:  # 新增通信循环,可以不断的通信,收发消息
        try:  # 在windows上，如果client突然终止，服务端就会出现异常，
            # 就需要加异常处理，但是在linux机器上不需要加异常处理
            msg = conn.recv(BUFSIZE)  # 听消息,听话,recv是从内核态内存中取字节
            if len(msg) == 0:  # 这条break是MAC系统的解决方式,就不需要异常处理
                break  # 如果不加,那么正在链接的客户端突然断开,recv便不再阻塞,死循环发生
            # print(msg, type(msg))   # b'dir' <class 'bytes'>, 只能收发字节
            # conn.send(msg.upper())    # 发消息,说话
            conn.send(b'HTTP/1.1 200 OK\r\n\r\n')  # 表示约定了http 协议
            conn.send(b'<h1>hello xiaozhan</h1>')    # 也可以把内容放到文件里，用rb方式来读取，因为发送的是字节流
            conn.send(b'<a href="http://www.sogo.com">sogo</a>')    # 也可以把内容放到文件里，用rb方式来读取，因为发送的是字节流

        except Exception:
            break  # 异常处理结束,下面的conn.close()不会被执行
    # conn.close()                   # 挂电话
s.close()                         # 手机关机