import socket

client = socket.socket()
print("输出缓冲区大小", client.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))   # 输出缓冲区大小,8192字节
print("输入缓冲区大小", client.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))   # 输入缓冲区大小，8192字节

client.connect(('127.0.0.1', 9989))

while 1:
    ui = input('请输入指令:>>>').strip()
    if len(ui) < 0:
        continue
    if ui.upper() == 'Q':
        break
    client.send(ui.encode('utf-8'))
    message_size = int(client.recv(2048).decode('utf-8'))   # 接收信息，得到要接收的数据长度
    client.send(b'recv_ready')    # 给server端回一个确认信息

    recv_size = 0   # 收到的数据长度
    data = b''   # 要接收的实际数据内容
    while recv_size < message_size:
        data += client.recv(2048)   #
        data_len = len(data)
        print("data length is", data_len)
        recv_size += data_len     # 以ipconfig 为例，数据总长度834，循环第一次接收768字节,recv_size=768
        print("recv_size is", recv_size)

    print(data.decode('utf-8'))

    # 请输入指令: >> > ipconfig /all      ，数据总长度是2501字节,这时候必须设置recv buff是2048，才能连续执行成功
    # 所以解决粘包的根本办法是增加接收端buffer
  # 第一轮循环：data_len = 768, recv_size = 768
  # 第二轮循环, data_len = 1536, recv_size = 2304
  # 第三轮循环, data_len = 2304, recv_size = 4608
