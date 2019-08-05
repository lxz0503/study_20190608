import socket

server = socket.socket()
server.bind(('127.0.0.1',7878))

server.listen(5)
print(server.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))  # 输出缓冲区大小,8192字节
print(server.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))  # 输入缓冲区大小，8192字节

conn, addr = server.accept()
print(conn, addr)

data1 = conn.recv(1024)
data2 = conn.recv(1024)

print(data1.decode('utf-8'))
print(data2.decode('utf-8'))
conn.close()
server.close()

# 在这端看到的现象就是 收到数据包是这样的：  123abc
# 实际上client端是发送了两次，应该是 123   abc