#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/7/2022 9:11 AM
@file:5-2-send-recv-服务端支持多个客户端.py
@project:openpyxl_excel
"""
# send发送数据，应用程序调用操作系统接口，也就是先把数据发送到发送缓冲区（内存中一块区域），然后操作系统控制网卡发送数据
# recv，是操作系统通过网卡接收数据，把接收的数据写到接收缓冲区（内存区域），应用程序再从缓冲区读取数据
# 端口就是传输数据的通道，端口号相当于通道标识，就是如何找到这个通道
# TCP/IP只是一个协议栈，就像操作系统的运行机制一样，必须要具体实现，同时还要提供对外的操作接口。
# 这个就像操作系统会提供标准的编程接口，
# 比如win32编程接口一样，TCP/IP也要提供可供程序员做网络开发所用的接口，这就是Socket编程接口
# Socket是对TCP/IP协议的封装，Socket本身并不是协议，而是一个调用接口（API），通过Socket，我们才能使用TCP/IP协议
# https://blog.csdn.net/weixin_48307978/article/details/116420363
import socket
import threading

BUFSIZE = 1024


def handle_request(new_client,ip_port):   # 处理客户端请求
    while True:
        rev_data = new_client.recv(BUFSIZE)  # 听消息,听话,recv是从内核态内存中取字节
        print('接收数据长度是:', len(rev_data))
        if rev_data:
            # 对接收的数据进行解码变成字符串
            rev_content = rev_data.decode('gbk')
            print(f'接收数据内容是:{rev_content},来自于{ip_port}')
            send_content = '数据处理中'
            # 对发送数据进行编码
            send_data = send_content.encode('gbk')
            # 发送数据到客户端
            new_client.send(send_data)
        else:
            print('客户端下线:', ip_port)
            break    # 跳出循环，执行下面的new_client.close()
    new_client.close()


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 买手机, 只负责接收客户端请求，不负责发送和接收数据
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 重用ip和端口
    s.bind(('127.0.0.1', 8000))  # 手机插卡
    s.listen(5)
    while True:
        new_client, ip_port = s.accept()   # 主线程循环等待客户端和服务端建立连接
        # 当连接建立后，创建子线程，专门处理接收客户端的消息
        sub_thread = threading.Thread(target=handle_request, args=(new_client, ip_port))
        # 设置守护主线程，主线程退出后子线程也自动推出
        sub_thread.setDaemon(True)
        sub_thread.start()
    # s.close()      # 手机关机，不再接收客户端请求，但是需要一直运行，可以注释掉这行代码

