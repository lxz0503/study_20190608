from socket import *
import struct
import time
import json
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
        try:
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
            result = (res.stderr.read() + res.stdout.read()).decode('gbk').encode('utf-8')    # 注意是utf-8,client必须用utf-8来解码
            # 4.获得真实数据的字节长度
            total_res_bytes = len(result)
            # 5.自定制字典报头
            head_dic = {
                'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'size': total_res_bytes,     # 字节长度
                'MD5': '8f6fbf8347faa4924a76856701edb0f3',
                'file_name': 'badminton.txt',
               }
            # 6. 序列化字典 ,并将其转换成字节形式
            head_dic_bytes = json.dumps(head_dic).encode('utf-8')
            # 7.使用 struct 封装报头字典head_dic_bytes ,固定长度(4个字节)
            # 封装成字节,发送给客户端,还是按照字节取出来.
            head = struct.pack('i', len(head_dic_bytes))
            # 8. 先将固定头发送给客户端
            conn.send(head)
            # 9 . 再将自定制报头发送给客户端
            conn.send(head_dic_bytes)
            # 10. 最后将真实结果发送给客户端
            conn.send(result)
            # 这里就是拼接字节
            # 格式: 固定头 + 自定义报头 +真实数据

            # 如果命令没有返回值，但是也能执行成功，例如cd ..
            if not result:
                result = "run command successfully"
                conn.send(result.encode('utf-8'))
            print("server端处理一条消息")
        except Exception:
            break
    conn.close()
tcp_socket_server.close()