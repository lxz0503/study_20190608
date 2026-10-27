#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/8/2022 7:06 PM
@file:5-10-搭建python自带静态web服务器.py
@project:openpyxl_excel
"""
import socket, os
import threading


class HttpWebServer(object):
    def __init__(self):
        self.buff_size = 1024
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 买手机, 只负责接收客户端请求，不负责发送和接收数据
        tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 重用ip和端口
        tcp_server_socket.bind(('', 8000))  # 手机插卡
        tcp_server_socket.listen(5)
        self.tcp_server_socket = tcp_server_socket

    @staticmethod      # 用不到当前类，完全是独立的函数
    def read_html(file_name):
        with open(file_name) as f:
            return f.read()

    def start_server(self):
        while True:
            new_client, ip_port = self.tcp_server_socket.accept()  # 主线程循环等待客户端和服务端建立连接
            # 当连接建立后，创建子线程，专门处理接收客户端的消息
            sub_thread = threading.Thread(target=self.handle_request, args=(new_client, ip_port))
            # 设置守护主线程，主线程退出后子线程也自动推出
            sub_thread.setDaemon(True)
            sub_thread.start()
        # self.tcp_server_socket.close()      # 手机关机，不再接收客户端请求，但是需要一直运行，可以注释掉这行代码

    def handle_request(self, new_client, ip_port):   # 处理客户端请求
        while True:
            rev_data = new_client.recv(self.buff_size)  # 听消息,听话,recv是从内核态内存中取字节
            print('接收数据长度是:', len(rev_data))
            if rev_data:
                # 对接收的数据进行解码变成字符串
                rev_content = rev_data.decode('utf-8')
                print(f'接收数据内容来自于{ip_port}')
                # 对数据按照空格进行分割,返回客户端指定的页面
                rev_list = rev_content.split(' ', maxsplit=2)   # 分割两次即可,查看返回内容就直到分割几次
                print(rev_list[1])    # /button.html
                req_path = rev_list[1]
                if req_path == '/':    # 如果访问的是根目录，则默认指向下面的页面
                    req_path = '/index.html'
                file_name = 'static' + req_path
                err_name = 'static' + '/error.html'
                # 处理发送数据，固定页面的话可以自己读取一个html文件的内容，写一个函数
                # 按照HTTP协议拼接数据:  相应行+响应头+空行+响应体
                if os.path.exists(file_name):
                    response_line = 'HTTP/1.1 200 OK\r\n'
                    response_header = 'Server: niginx\r\n'
                    response_body = self.read_html(file_name)
                    send_data = (response_line + response_header + '\r\n' + response_body).encode('utf-8')
                    new_client.send(send_data)
                else:    # 处理404 Not Found
                    response_line = 'HTTP/1.1 404 NOt Found\r\n'
                    response_header = 'Server: niginx\r\n'
                    response_body = self.read_html(err_name)
                    send_data = (response_line + response_header + '\r\n' + response_body).encode('utf-8')
                    new_client.send(send_data)
            else:    # 如果接收数据长度为0，表示没有数据，其实可能是刷新
                print('客户端下线:', ip_port)
                break             # 跳出循环，执行下面的new_client.close()
        new_client.close()


if __name__ == '__main__':
    run = HttpWebServer()
    run.start_server()





