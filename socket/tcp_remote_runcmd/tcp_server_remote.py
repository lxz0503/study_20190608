from socket import *
import subprocess

ip_port = ('127.0.0.1', 8080)
BUFSIZE = 1024

tcp_socket_server = socket(AF_INET, SOCK_STREAM)
tcp_socket_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
tcp_socket_server.bind(ip_port)
tcp_socket_server.listen(5)

while True:
    print("server 开始运行，等待客户端连接")
    conn, addr = tcp_socket_server.accept()   # 等待连接
    print('客户端', addr)

    while True:
        print("server开始接受消息")
        cmd = conn.recv(BUFSIZE)
        if len(cmd) == 0:
            break
        print("接收到", cmd)
        res = subprocess.Popen(cmd.decode('utf-8'),  # 字节解码为字符串
                               shell=True,
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        # 解析命令的返回值
        stderr = res.stderr.read()
        stdout = res.stdout.read()
        # 把命令的执行结果发送出去
        conn.send(stderr)
        conn.send(stdout)
        print("server端处理一条消息")