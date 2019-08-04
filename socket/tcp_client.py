import socket
ip_port = ('127.0.0.1', 8081)
BUFSIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect_ex(ip_port)                   # 拨电话

while True:                             # 新增通信循环,客户端可以不断发收消息
    msg = input('>>: ').strip()
    if len(msg) == 0:      # 必须有空消息的判断和处理，否则会挂死
        continue
    print(type(msg.encode('utf-8')))      # 字符串编码变成网络能识别的二进制字节 <class 'bytes'>
    s.send(msg.encode('utf-8'))         # 发消息,说话(只能发送字节类型)

    feedback = s.recv(BUFSIZE)                           # 收消息,听话
    print("只能接受字节类型", type(feedback))     # 只能接受字节类型 <class 'bytes'>
    print(feedback.decode('utf-8'))            #
    print(type(feedback.decode('utf-8')))      # <class 'str'>

s.close()