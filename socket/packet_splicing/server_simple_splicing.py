import socket
import subprocess

server = socket.socket()
server.bind(('127.0.0.1', 9989))
server.listen(5)
print("server输出缓冲区大小", server.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))  # 输出缓冲区大小,8192字节
print("server输入缓冲区大小", server.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))  # 输入缓冲区大小，8192字节

while 1:
    print("server starts:")
    conn, addr = server.accept()
    print(conn, addr)

    while 1:
        try:
            cmd = conn.recv(1024).decode('utf-8')
            if len(cmd) == 0:
                break
            print("cmd is", cmd)
            obj = subprocess.Popen(cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            result = (obj.stdout.read()+obj.stderr.read()).decode('gbk').encode('utf-8')  # 得到命令执行结果，编码为utf-8
            print("result length is", str(len(result)))
            conn.send(str(len(result)).encode('utf-8'))    # server先发送 数据长度 告诉client端

            data = conn.recv(1024).decode('utf-8')
            if data == 'recv_ready':
                conn.sendall(result)
        except Exception:
            break
    conn.close()
server.close()